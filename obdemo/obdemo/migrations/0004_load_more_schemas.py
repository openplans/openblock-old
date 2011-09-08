# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("db", "0014__undo_0009"),
        ("db", "0015_auto__add_field_schema_map_icon_url__add_field_schema_map_color"),

    )
    
    needed_by = (
        ("db", "0016_use_slug_fields_for_slugs"),
    )
    

    def forwards(self, orm):
        def _create_or_update(model_id, key, attributes):
            Model = orm[model_id]
            params = {'defaults': attributes}
            params.update(key)
            ob, created = Model.objects.get_or_create(**params)
            for k, v in attributes.items(): 
                setattr(ob, k, v)
            ob.save()
        
        
        _create_or_update('db.schema', {'slug': 'restaurant-inspections'}, {
            "is_special_report": False,
            "plural_name": "Restaurant Inspections",
            "last_updated": "2010-10-20",
            "name": "Restaurant Inspection",
            "has_newsitem_detail": True,
            "importance": 100,
            "uses_attributes_in_list": True,
            "min_date": "2009-01-01",
            "allow_charting": True,
            "can_collapse": True,
            "date_name": "Date",
            "indefinite_article": "a",
            "is_public": True,
            "number_in_overview": 5,
            "slug": "restaurant-inspections",
            "date_name_plural": "Dates",
            "grab_bag_headline": "",
            "short_source": "http://www.cityofboston.gov/isd/health/mfc/search.asp",
            "summary": "Restaurant Inspections",
            "source": "http://www.cityofboston.gov/isd/health/mfc/search.asp",
            "intro": "",
            "update_frequency": "",
            "short_description": "List of Restaurant Inspections",
            "grab_bag": ""
        })

        schema = orm['db.schema'].objects.get(slug='restaurant-inspections')
        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int02'}, {
            "is_lookup": False,
            "pretty_name_plural": "Inspection IDs",
            "is_charted": False,
            "name": "inspection_id",
            "display_order": 0,
            "is_searchable": False,
            "real_name": "int02",
            "pretty_name": "Inspection ID",
            "is_filter": False,
            "display": False,
            "schema": schema
        })
        
        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Restaurant IDs",
            "is_charted": False,
            "name": "restaurant_id",
            "display_order": 0,
            "is_searchable": False,
            "real_name": "int01",
            "pretty_name": "Restaurant ID",
            "is_filter": False,
            "display": False,
            "schema": schema
        })
            
        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Restaurant Names",
            "is_charted": False,
            "name": "restaurant_name",
            "display_order": 0,
            "is_searchable": True,
            "real_name": "varchar01",
            "pretty_name": "Restaurant Name",
            "is_filter": False,
            "display": True,
            "schema": schema
        })
        
        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int03'}, {
            "is_lookup": True,
            "pretty_name_plural": "Results",
            "is_charted": False,
            "name": "result",
            "display_order": 1,
            "is_searchable": False,
            "real_name": "int03",
            "pretty_name": "Result",
            "is_filter": True,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar02'}, {
            "is_lookup": True,
            "pretty_name_plural": "Violations",
            "is_charted": True,
            "name": "violation",
            "display_order": 2,
            "is_searchable": False,
            "real_name": "varchar02",
            "pretty_name": "Violation",
            "is_filter": True,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'text01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Violation Details",
            "is_charted": False,
            "name": "details",
            "display_order": 2,
            "is_searchable": False,
            "real_name": "text01",
            "pretty_name": "Violation Detail",
            "is_filter": False,
            "display": False,
            "schema": schema
        })

        _create_or_update("db.schema", {"slug": "police-reports"}, {
            "is_special_report": False,
            "plural_name": "Boston Police Department reports",
            "last_updated": "2010-10-21",
            "name": "Boston Police Department report",
            "has_newsitem_detail": True,
            "importance": 100,
            "uses_attributes_in_list": True,
            "min_date": "2009-01-01",
            "allow_charting": True,
            "can_collapse": True,
            "date_name": "Date",
            "indefinite_article": "a",
            "is_public": True,
            "number_in_overview": 5,
            "slug": "police-reports",
            "date_name_plural": "Dates",
            "grab_bag_headline": "",
            "short_source": "http://www.bpdnews.com",
            "summary": "Boston Police Department reports",
            "source": "http://www.bpdnews.com",
            "intro": "",
            "update_frequency": "",
            "short_description": "List of Boston Police Department reports",
            "grab_bag": ""
        })

        _create_or_update("db.schema", {"slug": "building-permits"}, {
            "is_special_report": False,
            "plural_name": "Building Permits",
            "last_updated": "2010-10-22",
            "name": "Building Permit",
            "has_newsitem_detail": True,
            "importance": 100,
            "uses_attributes_in_list": True,
            "min_date": "2009-01-01",
            "allow_charting": True,
            "can_collapse": True,
            "date_name": "Date",
            "indefinite_article": "a",
            "is_public": True,
            "number_in_overview": 5,
            "slug": "building-permits",
            "date_name_plural": "Dates",
            "grab_bag_headline": "",
            "short_source": "http://www.cityofboston.gov/isd/building/asofright/default.asp",
            "summary": "Boston Building Permits",
            "source": "http://www.cityofboston.gov/isd/building/asofright/default.asp",
            "intro": "",
            "update_frequency": "",
            "short_description": "List of Boston Building Permits",
            "grab_bag": ""
        })

        schema = orm['db.schema'].objects.get(slug='building-permits')

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Raw Addresses",
            "is_charted": False,
            "name": "raw_address",
            "display_order": 0,
            "is_searchable": False,
            "real_name": "varchar01",
            "pretty_name": "Raw Address",
            "is_filter": False,
            "display": False,
            "schema": schema
        })

        _create_or_update("db.schema", {"slug": "business-licenses"}, {
            "last_updated": "2011-04-05",
            "intro": "",
            "update_frequency": "",
            "has_newsitem_detail": True,
            "grab_bag_headline": "",
            "short_source": "",
            "slug": "business-licenses",
            "source": "",
            "date_name": "Date",
            "short_description": "",
            "grab_bag": "",
            "is_special_report": False,
            "importance": 0,
            "min_date": "1900-01-01",
            "allow_charting": False,
            "indefinite_article": "a",
            "is_public": True,
            "number_in_overview": 5,
            "date_name_plural": "Dates",
            "plural_name": "Business Licenses",
            "name": "Business License",
            "uses_attributes_in_list": False,
            "summary": "Business licenses in the city of Boston",
            "can_collapse": False
        })

        schema = orm['db.schema'].objects.get(slug='business-licenses')

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int01'}, {
            "is_lookup": True,
            "pretty_name_plural": "Business Types",
            "is_charted": False,
            "name": "business_type",
            "display_order": 10,
            "is_searchable": False,
            "real_name": "int01",
            "pretty_name": "Business Type",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar02'}, {
            "is_lookup": False,
            "pretty_name_plural": "File Numbers",
            "is_charted": False,
            "name": "file_number",
            "display_order": 10,
            "is_searchable": True,
            "real_name": "varchar02",
            "pretty_name": "File Number",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Names",
            "is_charted": False,
            "name": "name",
            "display_order": 10,
            "is_searchable": True,
            "real_name": "varchar01",
            "pretty_name": "Name",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar03'}, {
            "is_lookup": False,
            "pretty_name_plural": "Notes",
            "is_charted": False,
            "name": "notes",
            "display_order": 10,
            "is_searchable": False,
            "real_name": "varchar03",
            "pretty_name": "Notes",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schema", {"slug": "issues"}, {
            "is_special_report": False,
            "plural_name": "SeeClickFix Issues",
            "last_updated": "2010-10-22",
            "name": "SeeClickFix Issue",
            "has_newsitem_detail": True,
            "importance": 100,
            "uses_attributes_in_list": True,
            "min_date": "2009-01-01",
            "allow_charting": True,
            "can_collapse": True,
            "date_name": "Date",
            "indefinite_article": "a",
            "is_public": True,
            "number_in_overview": 5,
            "slug": "issues",
            "date_name_plural": "Dates",
            "grab_bag_headline": "",
            "short_source": "http://seeclickfix.com",
            "summary": "SeeClickFix Issues for Boston",
            "source": "http://seeclickfix.com/boston",
            "intro": "",
            "update_frequency": "",
            "short_description": "List of Issues in Boston, from SeeClickFix",
            "grab_bag": ""
        });

        schema = orm['db.schema'].objects.get(slug='issues')

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Ratings",
            "is_charted": False,
            "name": "rating",
            "display_order": 0,
            "is_searchable": False,
            "real_name": "int01",
            "pretty_name": "Rating",
            "is_filter": False,
            "display": True,
            "schema": schema
        })


        schema = orm['db.schema'].objects.get(slug='open311-service-requests')

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar03'}, {
            "is_lookup": False,
            "pretty_name_plural": "Address IDs",
            "is_charted": False,
            "name": "address_id",
            "display_order": 10,
            "is_searchable": False,
            "real_name": "varchar03",
            "pretty_name": "Address ID",
            "is_filter": False,
            "display": False,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'datetime02'}, {
            "is_lookup": False,
            "pretty_name_plural": "Expected Completion Dates",
            "is_charted": False,
            "name": "expected_datetime",
            "display_order": 4,
            "is_searchable": False,
            "real_name": "datetime02",
            "pretty_name": "Expected Completion Date",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar04'}, {
            "is_lookup": False,
            "pretty_name_plural": "Media URLs",
            "is_charted": False,
            "name": "media_url",
            "display_order": 10,
            "is_searchable": False,
            "real_name": "varchar04",
            "pretty_name": "Media URL",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Request IDs",
            "is_charted": False,
            "name": "service_request_id",
            "display_order": 10,
            "is_searchable": False,
            "real_name": "varchar01",
            "pretty_name": "Request ID",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'datetime01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Request Times",
            "is_charted": False,
            "name": "requested_datetime",
            "display_order": 5,
            "is_searchable": False,
            "real_name": "datetime01",
            "pretty_name": "Request Time",
            "is_filter": False,
            "display": True,
            "schema": schema
        })
        
        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int02'}, {
            "is_lookup": True,
            "pretty_name_plural": "Responsible Agencies",
            "is_charted": False,
            "name": "agency_responsible",
            "display_order": 6,
            "is_searchable": False,
            "real_name": "int02",
            "pretty_name": "Responsible Agency",
            "is_filter": True,
            "display": True,
            "schema": schema
        })
    
        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar02'}, {
            "is_lookup": False,
            "pretty_name_plural": "Service Codes",
            "is_charted": False,
            "name": "service_code",
            "display_order": 10,
            "is_searchable": False,
            "real_name": "varchar02",
            "pretty_name": "Service Code",
            "is_filter": False,
            "display": False,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int01'}, {
            "is_lookup": True,
            "pretty_name_plural": "Service Names",
            "is_charted": False,
            "name": "service_name",
            "display_order": 1,
            "is_searchable": False,
            "real_name": "int01",
            "pretty_name": "Service Name",
            "is_filter": True,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'text01'}, {
            "is_lookup": False,
            "pretty_name_plural": "Service Notices",
            "is_charted": False,
            "name": "service_notice",
            "display_order": 10,
            "is_searchable": False,
            "real_name": "text01",
            "pretty_name": "Service Notice",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'int03'}, {
            "is_lookup": True,
            "pretty_name_plural": "Statuses",
            "is_charted": False,
            "name": "status",
            "display_order": 2,
            "is_searchable": False,
            "real_name": "int03",
            "pretty_name": "Status",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

        _create_or_update("db.schemafield", {'schema': schema, 'real_name': 'varchar05'}, {
            "is_lookup": False,
            "pretty_name_plural": "Status Notes",
            "is_charted": False,
            "name": "status_notes",
            "display_order": 3,
            "is_searchable": False,
            "real_name": "varchar05",
            "pretty_name": "Status Notes",
            "is_filter": False,
            "display": True,
            "schema": schema
        })

    def backwards(self, orm):
        pass

    models = {
        'db.aggregateall': {
            'Meta': {'object_name': 'AggregateAll'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'total': ('django.db.models.fields.IntegerField', [], {})
        },
        'db.aggregateday': {
            'Meta': {'object_name': 'AggregateDay'},
            'date_part': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'total': ('django.db.models.fields.IntegerField', [], {})
        },
        'db.aggregatefieldlookup': {
            'Meta': {'object_name': 'AggregateFieldLookup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lookup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Lookup']"}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'schema_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.SchemaField']"}),
            'total': ('django.db.models.fields.IntegerField', [], {})
        },
        'db.aggregatelocation': {
            'Meta': {'object_name': 'AggregateLocation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Location']"}),
            'location_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.LocationType']"}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'total': ('django.db.models.fields.IntegerField', [], {})
        },
        'db.aggregatelocationday': {
            'Meta': {'object_name': 'AggregateLocationDay'},
            'date_part': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Location']"}),
            'location_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.LocationType']"}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'total': ('django.db.models.fields.IntegerField', [], {})
        },
        'db.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'bool01': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'bool02': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'bool03': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'bool04': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'bool05': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'date01': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date02': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date03': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date04': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date05': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'datetime01': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'datetime02': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'datetime03': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'datetime04': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'int01': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int02': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int03': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int04': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int05': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int06': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int07': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'news_item': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['db.NewsItem']", 'unique': 'True', 'primary_key': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'text01': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text02': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'time01': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time02': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'varchar01': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'varchar02': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'varchar03': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'varchar04': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'varchar05': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'})
        },
        'db.dataupdate': {
            'Meta': {'object_name': 'DataUpdate'},
            'got_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_added': ('django.db.models.fields.IntegerField', [], {}),
            'num_changed': ('django.db.models.fields.IntegerField', [], {}),
            'num_deleted': ('django.db.models.fields.IntegerField', [], {}),
            'num_skipped': ('django.db.models.fields.IntegerField', [], {}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'update_finish': ('django.db.models.fields.DateTimeField', [], {}),
            'update_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'db.location': {
            'Meta': {'ordering': "('slug',)", 'unique_together': "(('slug', 'location_type'),)", 'object_name': 'Location'},
            'area': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'centroid': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_order': ('django.db.models.fields.SmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_mod_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.GeometryField', [], {'null': 'True'}),
            'location_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.LocationType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'normalized_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'db.locationsynonym': {
            'Meta': {'object_name': 'LocationSynonym'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Location']"}),
            'normalized_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'db.locationtype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'LocationType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_browsable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_significant': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'plural_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'db.lookup': {
            'Meta': {'ordering': "('slug',)", 'unique_together': "(('slug', 'schema_field'),)", 'object_name': 'Lookup'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'schema_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.SchemaField']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'db.newsitem': {
            'Meta': {'ordering': "('title',)", 'object_name': 'NewsItem'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.Block']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.GeometryField', [], {'null': 'True', 'blank': 'True'}),
            'location_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'location_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Location']", 'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'db.newsitemlocation': {
            'Meta': {'unique_together': "(('news_item', 'location'),)", 'object_name': 'NewsItemLocation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Location']"}),
            'news_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.NewsItem']"})
        },
        'db.schema': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Schema'},
            'allow_charting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_collapse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_name': ('django.db.models.fields.CharField', [], {'default': "'Date'", 'max_length': '32'}),
            'date_name_plural': ('django.db.models.fields.CharField', [], {'default': "'Dates'", 'max_length': '32'}),
            'grab_bag': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'grab_bag_headline': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'has_newsitem_detail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'indefinite_article': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'intro': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_special_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_updated': ('django.db.models.fields.DateField', [], {}),
            'map_color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'map_icon_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'min_date': ('django.db.models.fields.DateField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'number_in_overview': ('django.db.models.fields.SmallIntegerField', [], {'default': '5'}),
            'plural_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'short_source': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'source': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'update_frequency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'uses_attributes_in_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'db.schemafield': {
            'Meta': {'ordering': "('pretty_name',)", 'unique_together': "(('schema', 'real_name'),)", 'object_name': 'SchemaField'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_order': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_charted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_filter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_lookup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_searchable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'pretty_name_plural': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"})
        },
        'db.searchspecialcase': {
            'Meta': {'object_name': 'SearchSpecialCase'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'redirect_to': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'streets.block': {
            'Meta': {'ordering': "('pretty_name',)", 'object_name': 'Block', 'db_table': "'blocks'"},
            'from_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'left_from_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'left_state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'db_index': 'True'}),
            'left_to_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'left_zip': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'postdir': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'predir': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'right_city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'right_from_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'right_state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'db_index': 'True'}),
            'right_to_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'right_zip': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'street_pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'street_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'to_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        }
    }


    complete_apps = ['obdemo', 'db']
