#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

from ebpub.db.models import Lookup, SchemaField, Schema
from ebpub.utils.text import smart_title
import re
import os.path

codes = re.compile(r"^([A-Z0-9]{3})\s+([0-9A-Z*]{1,2})\s+(.+)$").findall
schema = Schema.objects.get(slug="liquor-licenses")
schema_field = SchemaField.objects.get(schema=schema, name="license_class")
try:
    f = open(os.path.join(os.path.dirname(__file__), "codes.txt"))
    for line in f:
        class_code, license_type, name = codes(line[:-1])[0]
        name = " / ".join([smart_title(s, ["O.P."]).strip() for s in name.split("/")])
        lookup, created = Lookup.objects.get_or_create(
            schema_field=schema_field,
            name=name,
            code=class_code+"-"+license_type
        )
        if created:
            print "Created %r" % lookup
finally:
    f.close()
