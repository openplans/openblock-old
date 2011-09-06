from django.contrib.gis import geos
from django.test import TestCase
from ebpub.streets.models import Block, Place, PlaceSynonym, PlaceType
from ebpub.accounts.models import User
from ebpub.accounts.utils import test_client_login
from StringIO import StringIO
import mock
import csv

class TestPlaces(TestCase):
    
    import_url = '/admin/streets/place/import/csv'
    export_url = '/admin/streets/place/export/csv'
    
    fixtures = ['wabash.yaml']
    
    def setUp(self):
        # create a superuser to access admin views
        User.objects.create_superuser('admin@example.org', password='123')

    def test_import_csv(self):
        """
        test importing a csv full of places with no errors
        """
        
        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0\nDonut House,124 Fakey St.,1.001,2.001")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001
        
    def test_import_csv_synonyms(self):
        """
        test importing synonyms
        """
        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0,,Big Dough, Dough Mo\nDonut House,124 Fakey St.,1.001,2.001,,House of D, D House")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        
        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'BIG DOUGH' in synonyms
        assert 'DOUGH MO' in synonyms

                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'D HOUSE' in synonyms
        assert 'HOUSE OF D' in synonyms

    def test_import_csv_synonym_change(self):
        """
        test changing synonyms via import
        """

        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0,,Big Dough, Dough Mo\nDonut House,124 Fakey St.,1.001,2.001,,House of D, D House")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        
        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'BIG DOUGH' in synonyms
        assert 'DOUGH MO' in synonyms

                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'D HOUSE' in synonyms
        assert 'HOUSE OF D' in synonyms

        # now change one synonym of each
        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0,,Ole Doughy, Dough Mo\nDonut House,124 Fakey St.,1.001,2.001,,Dunky H, D House")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        
        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'OLE DOUGHY' in synonyms
        assert 'DOUGH MO' in synonyms

                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'DUNKY H' in synonyms
        assert 'D HOUSE' in synonyms
        


    def test_import_csv_no_location(self):
        """
        tests locationless places are not imported.
        """
        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0\nFlapper Jacks,,,,\nDonut House,124 Fakey St.,1.001,2.001\nSoup Sacks,,,")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001

    @mock.patch('ebpub.streets.models.get_metro')
    def test_import_csv_geocoding(self, mock_get_metro):
        """
        tests importing some locations with only 
        addresses specified
        """
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}

        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Arms Hotel, 205 South Wabash St.,,")
        csv_file.name = 'test.csv'

        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 1
        
        place = Place.objects.get(normalized_name='DONUT ARMS HOTEL')
        assert place.address == '205 South Wabash St.'
        assert place.location.x - -87.626153836734701 < 0.1
        assert place.location.y - 41.879488336734696 < 0.1

    @mock.patch('ebpub.streets.models.get_metro')    
    def test_import_csv_lat_lon_priority(self, mock_get_metro):
        """
        tests importing locations prioritizes 
        lat lon over address geocoding.
        """
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}

        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Arms Hotel, 205 South Wabash St.,1.0,2.0")
        csv_file.name = 'test.csv'

        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 1
        
        place = Place.objects.get(normalized_name='DONUT ARMS HOTEL')
        assert place.address == '205 South Wabash St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0


    def test_import_csv_changes_place_types(self):
        """
        test importing a place that changes a placetype
        """
        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 1
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        assert place.place_type.id == 1

        new_type = PlaceType(name='ZZZZ', plural_name='ZZZZs', 
                             indefinite_article='a', slug='funhouse',
                             is_geocodable=False, is_mappable=True)
        new_type.save()
        
        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '%d' % new_type.id, 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 1
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        assert place.place_type.id == new_type.id

    def test_export_csv(self):
        """
        test exporting a place type as csv
        """
        assert test_client_login(self.client, username='admin@example.org', password='123') == True
        
        place_type = PlaceType.objects.get(slug='poi')
        place = Place(pretty_name='Donut Palace', place_type=place_type,
                      address='100 Bubble Street', location=geos.Point(1.0, 2.0))
        place.save()
        place = Place(pretty_name='Donut Sanctuary', place_type=place_type,
                      address='101 Bubble Street', location=geos.Point(3.0, 4.0),
                      url='http://www.example.org/bs')
        place.save()

        
        response = self.client.post(self.export_url, {'place_type': place_type.id})
        assert response.status_code == 200
        
        rows = csv.reader(StringIO(response.content))
        
        count = 0
        for row in rows:
            assert len(row) == 5
            if row[0] == 'Donut Palace':
                assert row[1] == '100 Bubble Street'
                assert row[2] == '2.0'
                assert row[3] == '1.0'
                assert row[4] == ''       
            elif row[0] == 'Donut Sanctuary':
                assert row[1] == '101 Bubble Street'
                assert row[2] == '4.0'
                assert row[3] == '3.0'
                assert row[4] == 'http://www.example.org/bs'
            else: 
                assert 0, 'Unexpected Place!'       
            count += 1
            
        assert count == 2
        

    def test_export_csv_synonyms(self):
        """
        test exporting a place with synonyms
        """
        assert test_client_login(self.client, username='admin@example.org', password='123') == True
        
        place_type = PlaceType.objects.get(slug='poi')
        place = Place(pretty_name='Donut Palace', place_type=place_type,
                      address='100 Bubble Street', location=geos.Point(1.0, 2.0))
        place.save()
        ps = PlaceSynonym(pretty_name='Donut Hole', place=place)
        ps.save()
        ps = PlaceSynonym(pretty_name='Donut Pally', place=place)
        ps.save()
        
    
        place = Place(pretty_name='Donut Sanctuary', place_type=place_type,
                      address='101 Bubble Street', location=geos.Point(3.0, 4.0),
                      url='http://www.example.org/bs')
        place.save()
        ps = PlaceSynonym(pretty_name='Sancy D', place=place)
        ps.save()
        ps = PlaceSynonym(pretty_name='D Sanc', place=place)
        ps.save()
        
        response = self.client.post(self.export_url, {'place_type': place_type.id})
        assert response.status_code == 200
        
        rows = csv.reader(StringIO(response.content))
        
        count = 0
        for row in rows:
            assert len(row) == 7
            synonyms = set(row[5:])
            if row[0] == 'Donut Palace':
                assert row[1] == '100 Bubble Street'
                assert row[2] == '2.0'
                assert row[3] == '1.0'
                assert row[4] == ''
                assert 'Donut Hole' in synonyms
                assert 'Donut Pally' in synonyms
            elif row[0] == 'Donut Sanctuary':
                assert row[1] == '101 Bubble Street'
                assert row[2] == '4.0'
                assert row[3] == '3.0'
                assert row[4] == 'http://www.example.org/bs'
                assert 'Sancy D' in synonyms
                assert 'D Sanc' in synonyms
            else: 
                assert 0, 'Unexpected Place!'       
            count += 1
            
        assert count == 2
        
        
    def test_import_export(self):
        """
        tests that the results of an export can be imported
        """
        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0\nFlapper Jacks,,,,\nDonut House,124 Fakey St.,1.001,2.001,http://www.example.org/bs\nSoup Sacks,,,")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001
        assert place.url == 'http://www.example.org/bs'

        response = self.client.post(self.export_url, {'place_type': place.place_type.id})
        assert response.status_code == 200
        
        Place.objects.all().delete()
        assert Place.objects.all().count() == 0

        csv_file = StringIO(response.content)
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001
        assert place.url == 'http://www.example.org/bs'
        
        

    def test_import_export_synonyms(self):
        """
        tests that the results of an export can be imported
        including synonyms
        """

        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True


        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0,,Big Dough, Dough Mo\nDonut House,124 Fakey St.,1.001,2.001,http://www.example.org/bs,House of D, D House")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        
        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'BIG DOUGH' in synonyms
        assert 'DOUGH MO' in synonyms
        
                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001
        
        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'D HOUSE' in synonyms
        assert 'HOUSE OF D' in synonyms


        response = self.client.post(self.export_url, {'place_type': place.place_type.id})
        assert response.status_code == 200
        
        Place.objects.all().delete()
        assert Place.objects.all().count() == 0

        csv_file = StringIO(response.content)
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200
        
        assert Place.objects.all().count() == 2
        
        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0
        
        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'BIG DOUGH' in synonyms
        assert 'DOUGH MO' in synonyms
        
                
        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001
        
        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'D HOUSE' in synonyms
        assert 'HOUSE OF D' in synonyms


    def test_import_same_name(self):
        """
        tests that the importer can handle places with the same name.
        """

        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0,http://www.example.org/bs/0\nDonut Mountain,99 Fakley St.,99.0,22.0,http://www.example.org/bs/1")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200

        assert Place.objects.all().count() == 2

        locs = []
        for place in Place.objects.filter(normalized_name='DONUT MOUNTAIN').all():
            locs.append((place.address, place.location.x, place.location.y, place.url))

        assert ('123 Fakey St.', 2.0, 1.0, 'http://www.example.org/bs/0') in locs
        assert ('99 Fakley St.', 22.0, 99.0, 'http://www.example.org/bs/1') in locs
        
        

    def test_import_same_name_synonym(self):
        """
        tests that the importer can handle places with the same name.
        and maintain separate synonym lists.
        """

        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0,http://www.example.org/bs/0,123 D House, Mount D\nDonut Mountain,99 Fakley St.,99.0,22.0,http://www.example.org/bs/1,99 D House, Mount D")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200

        assert Place.objects.all().count() == 2

        locs = []
        for place in Place.objects.filter(normalized_name='DONUT MOUNTAIN').all():
            synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
            ll = [place.address, place.location.x, place.location.y, place.url]
            ll.extend(sorted(synonyms))
            locs.append(tuple(ll))

        assert ('123 Fakey St.', 2.0, 1.0, 'http://www.example.org/bs/0', '123 D HOUSE', 'MOUNT D') in locs
        assert ('99 Fakley St.', 22.0, 99.0, 'http://www.example.org/bs/1', '99 D HOUSE', 'MOUNT D') in locs



    def test_import_update_synonyms(self):
        """
        tests that the results of an export can be re-imported'
        to modify things, and no duplicates are formed.
        """

        assert Place.objects.all().count() == 0
        assert test_client_login(self.client, username='admin@example.org', password='123') == True

        csv_file = StringIO("Donut Mountain,123 Fakey St.,1.0,2.0,,Big Dough, Dough Mo\nDonut House,124 Fakey St.,1.001,2.001,http://www.example.org/bs,House of D, D House")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200

        assert Place.objects.all().count() == 2

        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'BIG DOUGH' in synonyms
        assert 'DOUGH MO' in synonyms


        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'D HOUSE' in synonyms
        assert 'HOUSE OF D' in synonyms

        # re-import
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200

        assert Place.objects.all().count() == 2

        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '123 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'BIG DOUGH' in synonyms
        assert 'DOUGH MO' in synonyms


        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'D HOUSE' in synonyms
        assert 'HOUSE OF D' in synonyms

        # re-import change an address slightly, change synonyms
        csv_file = StringIO("Donut Mountain,121 Fakey St.,1.0,2.0,,Big Doughy, Dough Mo\nDonut House,124 Fakey St.,1.001,2.001,http://www.example.org/bs, D House,Meye Donuts")
        csv_file.name = 'test.csv'
        response = self.client.post(self.import_url, {'place_type': '1', 'csv_file': csv_file})
        assert response.status_code == 200

        assert Place.objects.all().count() == 2

        place = Place.objects.get(normalized_name='DONUT MOUNTAIN')
        assert place.address == '121 Fakey St.'
        assert place.location.x == 2.0
        assert place.location.y == 1.0

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'BIG DOUGHY' in synonyms
        assert 'DOUGH MO' in synonyms


        place = Place.objects.get(normalized_name='DONUT HOUSE')
        assert place.address == '124 Fakey St.'
        assert place.location.x == 2.001
        assert place.location.y == 1.001

        synonyms = set([x.normalized_name for x in PlaceSynonym.objects.filter(place=place).all()])
        assert len(synonyms) == 2
        assert 'D HOUSE' in synonyms
        assert 'HOUSE OF D' not in synonyms
        assert 'MEYE DONUTS' in synonyms
        


class TestBlocks(TestCase):

    fixtures = ['wabash.yaml']
    urls = 'ebpub.urls'

    def test_contains_number__no_numbers(self):
        block = Block.objects.get(street='WABASH', pk=1002)
        for i in range(16):
            i = i ** i
            self.assertEqual(block.contains_number(i),
                             (False, None, None))


    def test_contains_number__no_left_or_right(self):
        block = Block.objects.get(street='WABASH', from_num=200, to_num=298)
        self.assertEqual(block.contains_number(200),
                         (True, 200, 298))
        self.assertEqual(block.contains_number(201),
                         (True, 200, 298))
        self.assertEqual(block.contains_number(298),
                         (True, 200, 298))
        self.assertEqual(block.contains_number(299),
                         (False, 200, 298))
        self.assertEqual(block.contains_number(199),
                         (False, 200, 298))

    def test_contains_number__left_and_righ(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.contains_number(214),
                         (False, 216, 298))
        self.assertEqual(block.contains_number(215),
                         (False, 217, 299))
        self.assertEqual(block.contains_number(216),
                         (True, 216, 298))
        self.assertEqual(block.contains_number(217),
                         (True, 217, 299))
        self.assertEqual(block.contains_number(298),
                         (True, 216, 298))
        self.assertEqual(block.contains_number(299),
                         (True, 217, 299))
        self.assertEqual(block.contains_number(300),
                         (False, 216, 298))

    def test_block__street_url(self):
        # TODO: these tests depend on get_metro()['multiple_cities'] setting
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.street_url(), '/streets/wabash-ave/')

    def test_block__rss_url(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.rss_url(), '/rss/streets/wabash-ave/216-299n-s/')


    def test_block__alert_url(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.alert_url(), '/streets/wabash-ave/216-299n-s/alerts/')


    def test_block__url(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.url(), '/streets/wabash-ave/216-299n-s/')
