from django.contrib.gis.gdal import DataSource
from ebpub.streets.models import Block
from ebpub.streets.name_utils import make_pretty_name
from ebpub.streets.name_utils import make_block_numbers
from ebpub.utils.text import slugify

class BlockImporter(object):
    def __init__(self, shapefile, layer_id=0):
        self.layer = DataSource(shapefile)[layer_id]

    def save(self, verbose=True):
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
                    block = Block(**block_fields)
                    block.geom = feature.geom.geos
                    (block.from_num, block.to_num) = make_block_numbers(
                        block_fields['left_from_num'],
                        block_fields['left_to_num'],
                        block_fields['right_from_num'],
                        block_fields['right_to_num'])

                    street_name, block_name = make_pretty_name(
                        block_fields['left_from_num'],
                        block_fields['left_to_num'],
                        block_fields['right_from_num'],
                        block_fields['right_to_num'],
                        block_fields['predir'],
                        block_fields['street'],
                        block_fields['suffix'],
                        block_fields['postdir']
                    )
                    block.pretty_name = block_name
                    block.street_pretty_name = street_name
                    block.street_slug = slugify(' '.join((block_fields['street'], block_fields['suffix'])))
                    block.save()
                    if parent_id is None:
                        parent_id = block.id
                    else:
                        block.parent_id = parent_id
                        block.save()
                    num_created += 1
                    if verbose:
                        print '%d\tCreated block %s for feature %d' % (num_created, block, feature.get('TLID'))
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

