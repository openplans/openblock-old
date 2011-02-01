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

import re
import string
import sys
import optparse
from django.contrib.gis.gdal import DataSource
from ebpub.metros.models import Metro
from ebpub.streets.models import Block
from ebpub.streets.name_utils import make_pretty_name
from ebpub.streets.name_utils import make_block_numbers
from ebpub.utils.text import slugify

FIELD_MAP = {
    # ESRI        # Block
    'L_F_ADD'   : 'left_from_num',
    'L_T_ADD'   : 'left_to_num',
    'R_F_ADD'   : 'right_from_num',
    'R_T_ADD'   : 'right_to_num',
    'POSTAL_L'  : 'left_zip',
    'POSTAL_R'  : 'right_zip',
    'GEONAME_L' : 'left_city',
    'GEONAME_R' : 'right_city',
    'STATE_L'   : 'left_state',
    'STATE_R'   : 'right_state',
}

NAME_FIELD_MAP = {
    'NAME'      : 'street',
    'TYPE'      : 'suffix',
    'PREFIX'    : 'predir',
    'SUFFIX'    : 'postdir',
}

# FCC == feature classification code: indicates the type of road
VALID_FCC_PREFIXES = (
    'A1', # primary highway with limited access
    'A2', # primary road without limited access
    'A3', # secondary and connecting road
    'A4'  # local, neighborhood, and rural road
)


class EsriImporter(object):
    # TODO: inherit from ebpub.streets.blockimport.base.BlockImporter ?

    def __init__(self, shapefile, city=None, layer_id=0, encoding='utf8',
                 verbose=False):
        self.verbose = verbose
        self.encoding = encoding
        ds = DataSource(shapefile)
        self.log("Opening %s" % shapefile)
        self.layer = ds[layer_id]
        self.city = city and city or Metro.objects.get_current().name
        self.fcc_pat = re.compile('^(' + '|'.join(VALID_FCC_PREFIXES) + ')\d$')

    def log(self, arg):
        if self.verbose:
            print >> sys.stderr, arg


    def save(self):
        alt_names_suff = (u'', u'1', u'2', u'3', u'4', u'5')
        num_created = 0
        for i, feature in enumerate(self.layer):
            if not self.fcc_pat.search(feature.get('FCC')):
                continue
            parent_id = None
            fields = {}
            for esri_fieldname, block_fieldname in FIELD_MAP.items():
                value = feature.get(esri_fieldname)
                if isinstance(value, basestring):
                    value = value.upper()
                elif isinstance(value, int) and value == 0:
                    value = None
                fields[block_fieldname] = value
            if not ((fields['left_from_num'] and fields['left_to_num']) or
                    (fields['right_from_num'] and fields['right_to_num'])):
                continue
            # Sometimes the "from" number is greater than the "to"
            # number in the source data, so we swap them into proper
            # ordering
            for side in ('left', 'right'):
                from_key, to_key = '%s_from_num' % side, '%s_to_num' % side
                if fields[from_key] > fields[to_key]:
                    fields[from_key], fields[to_key] = fields[to_key], fields[from_key]
            if feature.geom.geom_name != 'LINESTRING':
                continue
            for suffix in alt_names_suff:
                name_fields = {}
                for esri_fieldname, block_fieldname in NAME_FIELD_MAP.items():
                    key = esri_fieldname + suffix
                    name_fields[block_fieldname] = feature.get(key).upper()
                if not name_fields['street']:
                    continue
                # Skip blocks with bare number street names and no suffix / type
                if not name_fields['suffix'] and re.search('^\d+$', name_fields['street']):
                    continue
                fields.update(name_fields)

                # Ensure we have unicode.
                for key, val in fields.items():
                    if isinstance(val, str):
                        fields[key] = val.decode(self.encoding)

                fields['street_pretty_name'], fields['pretty_name'] = make_pretty_name(
                    fields['left_from_num'],
                    fields['left_to_num'],
                    fields['right_from_num'],
                    fields['right_to_num'],
                    fields['predir'],
                    fields['street'],
                    fields['suffix'],
                    fields['postdir'],
                )

                #print >> sys.stderr, 'Looking at block pretty name %s' % fields['street']

                fields['street_slug'] = slugify(u' '.join((fields['street'], fields['suffix'])))

                # Watch out for addresses like '247B' which can't be
                # saved as an IntegerField. But do this after making
                # pretty names.
                for addr_key in ('left_from_num', 'left_to_num', 'right_from_num', 'right_to_num'):
                    fields[addr_key] = fields[addr_key].rstrip(string.letters)

                fields['from_num'], fields['to_num'] = make_block_numbers(
                    fields['left_from_num'],
                    fields['left_to_num'],
                    fields['right_from_num'],
                    fields['right_to_num'])

                block = Block(**fields)
                block.geom = feature.geom.geos
                self.log(u'Looking at block %s' % fields['street'])

                block.save()
                if parent_id is None:
                    parent_id = block.id
                else:
                    block.parent_id = parent_id
                    block.save()
                num_created += 1
                self.log('Created block %s' % block)
        return num_created



def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = optparse.OptionParser(usage='%prog edges.shp')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      default=False)
    parser.add_option('-c', '--city', dest='city',
                      help='A city name to filter against', default=None)
    parser.add_option('-e', '--encoding', dest='encoding',
                      help='Encoding to use when reading the shapefile',
                      default='utf8')

    (options, args) = parser.parse_args(argv)
    if len(args) != 1:
        return parser.error('must provide at least 1 arguments, see usage')

    esri = EsriImporter(shapefile=args[0],
                        city=options.city, verbose=options.verbose,
                        encoding=options.encoding,
                        )
    num_created = esri.save()
    if options.verbose:
        print "Created %d blocks" % num_created

if __name__ == '__main__':
    sys.exit(main())
