#   Copyright 2012 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

from django.test import TestCase
from django.core.urlresolvers import reverse
import mock

class ViewSmokeTests(TestCase):

    # Just stupid smoke tests ... better than nothing.
    fixtures = ('crimes.json',)

    def _get_schema(self):
        from ebpub.db.models import Schema
        return Schema.objects.get(slug='crime')

    def _get_lookup(self):
        from ebpub.db.models import SchemaField
        lookup = SchemaField.objects.get(schema=self._get_schema(),
                                         is_lookup=True,
                                         name='beat')
        return lookup

    def test_index(self):
        url = reverse('admin:obadmin-old')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_schema_list(self):
        url = reverse('admin:old-schema-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_set_staff_cookie(self):
        url = reverse('admin:old-set-staff-cookie')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://testserver/admin/old/')

    def test_edit_schema_lookups(self):
        url = reverse('admin:old-edit-lookups',
                      args=(self._get_schema().id, self._get_lookup().id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_schemafield_list(self):
        url = reverse('admin:old-sf-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_geocoder_success_rates(self):
        url = reverse('admin:old-geocoder-success-rates')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_blob_seed_list(self):
        url = reverse('admin:old-blob-seed-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_blob_seed(self):
        url = reverse('admin:old-add-blob-seed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_scraper_history_list(self):
        url = reverse('admin:old-scraper-history-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_scraper_history_schema(self):
        url = reverse('admin:old-scraper-history-schema',
                      args=(self._get_schema().slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # TODO: This view is totally unused?
    # def test_newsitem_details(self):
    #     url = reverse()
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)

    def test_jobs_status(self):
        url = reverse('admin:jobs-status', 
                      kwargs={'appname': 'streets', 'modelname': 'blocks'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_zipcode_shapefiles(self):
        url = reverse('admin:import-zipcodes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_shapefile(self):
        url = reverse('admin:upload-shapefile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('obadmin.admin.views.DataSource')
    def test_pick_shapefile_layer(self, mock_datasource):
        url = reverse('admin:pick-shapefile-layer')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url += '?shapefile=blah'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_blocks(self):
        url = reverse('admin:import-blocks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_newsitems(self):
        url = reverse('admin:import-newsitems')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)










