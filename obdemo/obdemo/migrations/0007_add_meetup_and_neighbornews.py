# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("db", "0020_auto__add_field_schema_is_event"),
        ('neighbornews', '0002_add_is_event'),
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
            return ob

        # Meetups schema
        schema = _create_or_update(
            'db.schema', {'slug': 'meetups'},
            {
                "allow_charting": True,
                "can_collapse": False,
                "date_name": "Date",
                "date_name_plural": "Dates",
                "grab_bag": "",
                "grab_bag_headline": "",
                "has_newsitem_detail": True,
                "importance": 0,
                "indefinite_article": "a",
                "intro": "",
                "is_event": True,
                "is_public": True,
                "is_special_report": False,
                "last_updated": "2011-09-09",
                "min_date": "2011-01-01",
                "name": "Meetup",
                "number_in_overview": 5,
                "plural_name": "Meetups",
                "short_description": "Meetups",
                "short_source": "http://meetup.com",
                "slug": "meetups",
                "source": "http://meetup.com",
                "summary": "Local Meetup meetings",
                "update_frequency": "",
                "uses_attributes_in_list": True,
                })

        _create_or_update(
            'db.schemafield', {'schema': schema, 'name': "group_name",},
            {
                "display": True,
                "display_order": 1,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": True,
                "pretty_name": "Group Name",
                "pretty_name_plural": "Group Names",
                "real_name": "varchar01",
                })

        _create_or_update(
            'db.schemafield', {'schema': schema, 'name': "venue_name",},
            {
                "display": True,
                "display_order": 5,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": True,
                "pretty_name": "Venue Name",
                "pretty_name_plural": "Venue Names",
                "real_name": "varchar02",
                })

        _create_or_update(
            'db.schemafield', {'schema': schema, 'name': "venue_phone",},
            {
                "display": True,
                "display_order": 10,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": False,
                "pretty_name": "Venue Phone",
                "pretty_name_plural": "Venue Phones",
                "real_name": "varchar03",
                })

        _create_or_update(
            'db.schemafield', {'schema': schema, 'name': 'start_time',},
            {
                "display": True,
                "display_order": 0,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": False,
                "pretty_name": "Start Time",
                "real_name": "time01",
                })

        # Neighbornews schemas.
        schema = _create_or_update(
            'db.schema', {'slug': 'neighbor-events'},
            {
                "allow_charting": True,
                "allow_comments": True,
                "can_collapse": False,
                "date_name": "Date",
                "date_name_plural": "Dates",
                "grab_bag": "",
                "grab_bag_headline": "",
                "has_newsitem_detail": True,
                "importance": 0,
                "indefinite_article": "a",
                "intro": "",
                "is_public": True,
                "is_special_report": False,
                "last_updated": "2011-08-03",
                "map_color": "",
                "map_icon_url": "",
                "min_date": "2011-08-03",
                "name": "Neighbor Event",
                "number_in_overview": 5,
                "plural_name": "Neighbor Events",
                "short_description": "User contributed events",
                "short_source": "",
                "slug": "neighbor-events",
                "source": "",
                "summary": "",
                "update_frequency": "",
                "uses_attributes_in_list": False,
                'is_event': True,
                })
        _create_or_update(
            'db.schemafield', {"name": "categories", "schema": schema},
            {
                "display": True,
                "display_order": 10,
                "is_charted": False,
                "is_filter": True,
                "is_lookup": True,
                "is_searchable": False,
                "pretty_name": "Categories",
                "pretty_name_plural": "Categories",
                "real_name": "varchar01",
                })
        _create_or_update(
            'db.schemafield', {"name": "start_time", "schema": schema},
            {
                "display": True,
                "display_order": 24,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": False,
                "pretty_name": "Start Time",
                "pretty_name_plural": "Start Times",
                "real_name": "time01",
                })
        _create_or_update(
            'db.schemafield', {"name": "end_time", "schema": schema},
            {
                "display": True,
                "display_order": 25,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": False,
                "pretty_name": "End Time",
                "pretty_name_plural": "End Times",
                "real_name": "time02",
                })

        _create_or_update(
            'db.schemafield', {"name": "image_url", "schema": schema},
            {
                "display": False,
                "display_order": 10,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": False,
                "pretty_name": "Image URL",
                "pretty_name_plural": "Image URLs",
                "real_name": "text01",
                })

        # Neighbornews neighbor-messages schema.
        schema = _create_or_update(
            'db.schema', {'slug': 'neighbor-messages'},
            {
                "allow_charting": True,
                "allow_comments": True,
                "can_collapse": False,
                "date_name": "Date",
                "date_name_plural": "Dates",
                "grab_bag": "",
                "grab_bag_headline": "",
                "has_newsitem_detail": True,
                "importance": 0,
                "indefinite_article": "a",
                "intro": "",
                "is_public": True,
                "is_special_report": False,
                "last_updated": "2011-08-03",
                "map_color": "",
                "map_icon_url": "",
                "min_date": "2011-08-03",
                "name": "Neighbor Message",
                "number_in_overview": 5,
                "plural_name": "Neighbor Messages",
                "short_description": "User contributed messages and news",
                "short_source": "",
                "slug": "neighbor-messages",
                "source": "",
                "summary": "",
                "update_frequency": "",
                "uses_attributes_in_list": False,
                'is_event': False,
                })

        _create_or_update(
            'db.schemafield', {"name": "categories", "schema": schema},
            {
                "display": True,
                "display_order": 10,
                "is_charted": False,
                "is_filter": True,
                "is_lookup": True,
                "is_searchable": False,
                "pretty_name": "Categories",
                "pretty_name_plural": "Categories",
                "real_name": "varchar01",
                })

        _create_or_update(
            'db.schemafield', {"name": "image_url", "schema": schema},
            {
                "display": False,
                "display_order": 10,
                "is_charted": False,
                "is_filter": False,
                "is_lookup": False,
                "is_searchable": False,
                "pretty_name": "Image URL",
                "pretty_name_plural": "Image URLs",
                "real_name": "text01",
                })


    def backwards(self, orm):
        pass


    models = {
        'accounts.user': {
            'Meta': {'object_name': 'User', '_ormbases': ['auth.User']},
            'main_metro': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'})
        },
        'db.lookup': {
            'Meta': {'ordering': "('slug',)", 'unique_together': "(('slug', 'schema_field'),)", 'object_name': 'Lookup'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'schema_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.SchemaField']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'db.newsitem': {
            'Meta': {'ordering': "('title',)", 'object_name': 'NewsItem'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.Block']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'last_modification': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
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
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'is_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'short_source': ('django.db.models.fields.CharField', [], {'default': "'One-line description of where this information came from.'", 'max_length': '128', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
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
        'neighbornews.newsitemcreator': {
            'Meta': {'ordering': "('news_item',)", 'unique_together': "(('news_item', 'user'),)", 'object_name': 'NewsItemCreator'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'news_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.NewsItem']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']"})
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

    complete_apps = ['db', 'neighbornews', 'obdemo']
