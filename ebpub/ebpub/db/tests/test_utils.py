#   Copyright 2011 OpenPlans, and contributors
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

from django.test import TestCase

class TestDoFilterUrl(TestCase):

    fixtures = ('crimes.json',)

    def test_populate_attributes_if_needed(self):

        from ebpub.db.models import NewsItem
        item = NewsItem.objects.get(title='crime title 1')
        ni_list = [item]

        # It's lazy - but just checking length is enough to trigger
        # attribute population.
        self.assert_(len(item.attributes) > 1)

        from ebpub.db.utils import populate_attributes_if_needed
        schema_list = list(set((ni.schema for ni in ni_list)))
        populate_attributes_if_needed(ni_list, schema_list)
        self.assert_(len(item.attributes) > 1)
        self.assertEqual(item.attributes['arrests'], False)
        self.assertEqual(item.attributes['case_number'], 'case number 1')

        # Get another reference to the same NewsItem and verify that
        # prepopulation and laziness give all the same results.
        ni2 = NewsItem.objects.get(title='crime title 1')
        self.failIf(item is ni2)
        ni2.attributes['beat']  # Triggers loading.
        for key, val in item.attributes.items():
            # ... well, mostly the same.
            # populate_attributes_if_needed() dereferences Lookups,
            # which lazy attribute lookup doesn't yet.  This is crazy,
            # but AttributesForTemplate handles both cases.
            from ebpub.db.models import Lookup
            if isinstance(val, Lookup):
                self.assertEqual(val.id, ni2.attributes[key])
            elif isinstance(val, list) and isinstance(val[0], Lookup):
                self.assertEqual(','.join([str(v.id) for v in val]),
                                 ni2.attributes[key])
            else:
                self.assertEqual(val, ni2.attributes[key])
