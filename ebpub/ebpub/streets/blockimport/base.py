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

import string
import sys
from django.contrib.gis.gdal import DataSource
from django.core.exceptions import ValidationError
from ebpub.streets.models import Block
from ebpub.streets.name_utils import make_pretty_name
from ebpub.streets.name_utils import make_block_numbers
from ebpub.utils.text import slugify

import logging
logger = logging.getLogger('ebpub.streets.blockimport')

class BlockImporter(object):
    def __init__(self, shapefile, layer_id=0, verbose=False, encoding='utf8'):
        self.layer = DataSource(shapefile)[layer_id]
        self.verbose = verbose
        self.encoding = encoding

    def log(self, arg):
        "Deprecated: user logger instead"
        if self.verbose:
            print >> sys.stderr, arg

    def save(self):
        num_created = 0
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

                    block_fields['geom'] = feature.geom.geos

                    block_fields['street_pretty_name'], block_fields['pretty_name'] = make_pretty_name(
                        block_fields['left_from_num'],
                        block_fields['left_to_num'],
                        block_fields['right_from_num'],
                        block_fields['right_to_num'],
                        block_fields['predir'],
                        block_fields['street'],
                        block_fields['suffix'],
                        block_fields['postdir']
                    )

                    block_fields['street_slug'] = slugify(u' '.join((block_fields['street'], block_fields['suffix'])))

                    # Watch out for addresses like '247B' which can't be
                    # saved as an IntegerField.
                    # But do this *after* making pretty names.
                    for addr_key in ('left_from_num', 'left_to_num',
                                     'right_from_num', 'right_to_num'):
                        if isinstance(block_fields[addr_key], basestring):
                            value = block_fields[addr_key].rstrip(string.letters)
                            # Also attempt to fix up addresses like
                            # '19-47', by just using the lower number.
                            # This will give misleading output, but
                            # it's probably better than discarding blocks.
                            value = value.split('-')[0]
                            if value:
                                try:
                                    value = int(value)
                                except ValueError:
                                    logger.warn("Omitting weird value %r for %r" % (value, addr_key))
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

                    block = Block(**block_fields)
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
                    num_created += 1
                    logger.debug('%d\tCreated block %s for feature %d' % (num_created, block, feature.get('TLID')))
        return num_created

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

