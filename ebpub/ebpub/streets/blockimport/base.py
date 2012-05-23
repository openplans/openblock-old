#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib.gis.gdal import DataSource
from django.core.exceptions import ValidationError
from ebpub.streets.models import Block
from ebpub.streets.name_utils import make_pretty_name
from ebpub.streets.name_utils import make_pretty_prefix
from ebpub.streets.name_utils import make_block_numbers
from ebpub.utils.geodjango import geos_with_projection
from ebpub.utils.text import slugify


import logging
logger = logging.getLogger('ebpub.streets.blockimport')

class BlockImporter(object):
    """
    Base class for importing blocks from shapefiles.

    Subclasses will implement the details for one particular data source.
    """
    def __init__(self, shapefile, layer_id=0, verbose=False, encoding='utf8',
                 reset=False,
                 ):
        self.layer = DataSource(shapefile)[layer_id]
        self.verbose = verbose
        self.encoding = encoding
        self.reset = reset

    def log(self, arg):
        "Deprecated: user logger instead"
        logger.debug(arg)

    def save(self):
        if self.reset:
            logger.warn("Deleting all Block instances and anything that refers to them!")
            Block.objects.all().delete()
        import time
        start = time.time()
        num_created = 0
        num_existing = 0
        for feature in self.layer:
            parent_id = None
            if not self.skip_feature(feature):
                for block_fields in self.gen_blocks(feature):

                    # Usually (at least in Boston data) there is only
                    # 1 block per feature.  But sometimes there are
                    # multiple names for one street, eg.
                    # "N. Commercial Wharf" and "Commercial Wharf N.";
                    # in that case those would be yielded by gen_blocks() as
                    # two separate blocks. Is that intentional, or a bug?

                    # Ensure we have unicode.
                    for key, val in block_fields.items():
                        if isinstance(val, str):
                            block_fields[key] = val.decode(self.encoding)

                    block_fields['geom'] = geos_with_projection(feature.geom, 4326)
                    block_fields['prefix'] = make_pretty_prefix(block_fields['prefix'])

                    block_fields['street_pretty_name'], block_fields['pretty_name'] = make_pretty_name(
                        block_fields['left_from_num'],
                        block_fields['left_to_num'],
                        block_fields['right_from_num'],
                        block_fields['right_to_num'],
                        block_fields['predir'],
                        block_fields['prefix'],
                        block_fields['street'],
                        block_fields['suffix'],
                        block_fields['postdir']
                    )

                    block_fields['street_slug'] = slugify(
                        u' '.join((block_fields['prefix'],
                                   block_fields['street'],
                                   block_fields['suffix'])))

                    # Watch out for addresses like '247B' which can't be
                    # saved as an IntegerField.
                    # But do this *after* making pretty names.
                    # Also attempt to fix up addresses like '19-47',
                    # by just using the lower number.  This will give
                    # misleading output, but it's probably better than
                    # discarding blocks.
                    for addr_key in ('left_from_num', 'left_to_num',
                                     'right_from_num', 'right_to_num'):
                        if isinstance(block_fields[addr_key], basestring):
                            from ebpub.geocoder.parser.parsing import number_standardizer
                            value = number_standardizer(block_fields[addr_key].strip())
                            if not value:
                                value = None
                        else:
                            value = None
                        block_fields[addr_key] = value

                    try:
                        block_fields['from_num'], block_fields['to_num'] = \
                            make_block_numbers(block_fields['left_from_num'],
                                               block_fields['left_to_num'],
                                               block_fields['right_from_num'],
                                               block_fields['right_to_num'])
                    except ValueError, e:
                        logger.warn('Skipping %s: %s' % (block_fields['pretty_name'], e))
                        continue

                    # After doing pretty names etc, standardize the fields
                    # that get used for geocoding, since the geocoder
                    # searches for the standardized version.
                    from ebpub.geocoder.parser.parsing import STANDARDIZERS
                    for key, standardizer in STANDARDIZERS.items():
                        if key in block_fields:
                            if key == 'street' and block_fields['prefix']:
                                # Special case: "US Highway 101", not "US Highway 101st".
                                continue

                            block_fields[key] = standardizer(block_fields[key])

                    # Separate out the uniquely identifying fields so
                    # we can avoid duplicate blocks.
                    # NOTE this doesn't work if you're updating from a more
                    # recent shapefile and the street has significant
                    # changes - eg. the street name has changed, or the
                    # address range has changed, or the block has split...
                    # see #257. http://developer.openblockproject.org/ticket/257
                    primary_fields = {}
                    primary_field_keys = ('street_slug',
                                          'from_num', 'to_num',
                                          'left_city', 'right_city',
                                          'left_zip', 'right_zip',
                                          'left_state', 'right_state',
                                          )
                    for key in primary_field_keys:
                        if block_fields[key] != u'':
                            # Some empty fields are fixed
                            # automatically by clean().
                            primary_fields[key] = block_fields[key]

                    existing = list(Block.objects.filter(**primary_fields))
                    if not existing:
                        # Check the old-style way we used to make street slugs
                        # prior to fixing issue #264... we need to keep this
                        # code around indefinitely in case we are reloading the
                        # blocks data and need to overwrite blocks that have
                        # the old bad slug.  Sadly this probably can't just be
                        # fixed by a migration.
                        _old_street_slug = slugify(
                            u' '.join((block_fields['street'],
                                       block_fields['suffix'])))
                        _old_primary_fields = primary_fields.copy()
                        _old_primary_fields['street_slug'] = _old_street_slug
                        existing = list(Block.objects.filter(**_old_primary_fields))
                        if not existing:
                            block = Block(**block_fields)
                            num_created += 1
                            logger.debug("CREATING %s" % unicode(block))

                    if len(existing) == 1:
                        num_existing += 1
                        block = existing[0]
                        logger.debug(u"Block %s already exists" % unicode(existing[0]))
                        for key, val in block_fields.items():
                            setattr(block, key, val)
                    elif len(existing) > 1:
                        num_existing += len(existing)
                        logger.warn("Multiple existing blocks like %s, skipping"
                                    % existing[0])
                        continue
                    try:
                        block.full_clean()
                    except ValidationError:
                        # odd bug: sometimes we get ValidationError even when
                        # the data looks good, and then cleaning again works???
                        try:
                            block.full_clean()
                        except ValidationError, e:
                            logger.warn("validation error on %s, skipping" % str(block))
                            logger.warn(e)
                            continue
                    block.save()
                    if parent_id is None:
                        parent_id = block.id
                    else:
                        block.parent_id = parent_id
                        block.save()
                    logger.debug('%d\tCreated block %s for feature %d' % (num_created, block, feature.fid))
        logger.info("Created %d new blocks in %.2f seconds" % (num_created,
                                                               time.time() - start))
        return num_created, num_existing

    def skip_feature(self, feature):
        """
        Subclasses can override this method to determine whether to
        skip this feature, for example, because the feature is not a
        street or is missing an address number.

        It could also be used to provide geometric filtering, for
        example, a subclass could inspect the geom attribute of the
        feature to determine if it is contained by a particular
        geometry.
        """
        return True

    def gen_blocks(self, feature):
        """
        A generator that yields dictionaries (of keys that are BLOCK_FIELDS)
        """
        raise NotImplementedError('subclass must implement this method')

