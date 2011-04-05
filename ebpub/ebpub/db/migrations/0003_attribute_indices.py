# encoding: utf-8
import datetime
from south.db import dbs
from south.v2 import DataMigration
from django.db import models
from django.db import router

def get_db(orm, model):
    dbname = router.db_for_write(orm[model])
    return dbs[dbname]

class Migration(DataMigration):

    def forwards(self, orm):
        "Add partial indexes for the value columns. We only want to index values that are not NULL."
        db = get_db(orm, 'db.Attribute')
        db.execute("CREATE INDEX db_attribute_varchar01 ON db_attribute (varchar01) WHERE varchar01 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_varchar02 ON db_attribute (varchar02) WHERE varchar02 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_varchar03 ON db_attribute (varchar03) WHERE varchar03 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_varchar04 ON db_attribute (varchar04) WHERE varchar04 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_varchar05 ON db_attribute (varchar05) WHERE varchar05 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_date01 ON db_attribute (date01) WHERE date01 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_date02 ON db_attribute (date02) WHERE date02 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_date03 ON db_attribute (date03) WHERE date03 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_date04 ON db_attribute (date04) WHERE date04 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_date05 ON db_attribute (date05) WHERE date05 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_time01 ON db_attribute (time01) WHERE time01 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_time02 ON db_attribute (time02) WHERE time02 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_datetime01 ON db_attribute (datetime01) WHERE datetime01 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_datetime02 ON db_attribute (datetime02) WHERE datetime02 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_datetime03 ON db_attribute (datetime03) WHERE datetime03 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_datetime04 ON db_attribute (datetime04) WHERE datetime04 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_bool01 ON db_attribute (bool01) WHERE bool01 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_bool02 ON db_attribute (bool02) WHERE bool02 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_bool03 ON db_attribute (bool03) WHERE bool03 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_bool04 ON db_attribute (bool04) WHERE bool04 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_bool05 ON db_attribute (bool05) WHERE bool05 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_int01 ON db_attribute (int01) WHERE int01 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_int02 ON db_attribute (int02) WHERE int02 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_int03 ON db_attribute (int03) WHERE int03 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_int04 ON db_attribute (int04) WHERE int04 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_int05 ON db_attribute (int05) WHERE int05 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_int06 ON db_attribute (int06) WHERE int06 IS NOT NULL;")
        db.execute("CREATE INDEX db_attribute_int07 ON db_attribute (int07) WHERE int07 IS NOT NULL;")


    def backwards(self, orm):
        "drop partial indices on attribue table"
        db = get_db(orm, 'db.Attribute')
        db.execute("DROP INDEX IF EXISTS db_attribute_varchar01;")
        db.execute("DROP INDEX IF EXISTS db_attribute_varchar02;")
        db.execute("DROP INDEX IF EXISTS db_attribute_varchar03;")
        db.execute("DROP INDEX IF EXISTS db_attribute_varchar04;")
        db.execute("DROP INDEX IF EXISTS db_attribute_varchar05;")
        db.execute("DROP INDEX IF EXISTS db_attribute_date01;")
        db.execute("DROP INDEX IF EXISTS db_attribute_date02;")
        db.execute("DROP INDEX IF EXISTS db_attribute_date03;")
        db.execute("DROP INDEX IF EXISTS db_attribute_date04;")
        db.execute("DROP INDEX IF EXISTS db_attribute_date05;")
        db.execute("DROP INDEX IF EXISTS db_attribute_time01;")
        db.execute("DROP INDEX IF EXISTS db_attribute_time02;")
        db.execute("DROP INDEX IF EXISTS db_attribute_datetime01;")
        db.execute("DROP INDEX IF EXISTS db_attribute_datetime02;")
        db.execute("DROP INDEX IF EXISTS db_attribute_datetime03;")
        db.execute("DROP INDEX IF EXISTS db_attribute_datetime04;")
        db.execute("DROP INDEX IF EXISTS db_attribute_bool01;")
        db.execute("DROP INDEX IF EXISTS db_attribute_bool02;")
        db.execute("DROP INDEX IF EXISTS db_attribute_bool03;")
        db.execute("DROP INDEX IF EXISTS db_attribute_bool04;")
        db.execute("DROP INDEX IF EXISTS db_attribute_bool05;")
        db.execute("DROP INDEX IF EXISTS db_attribute_int01;")
        db.execute("DROP INDEX IF EXISTS db_attribute_int02;")
        db.execute("DROP INDEX IF EXISTS db_attribute_int03;")
        db.execute("DROP INDEX IF EXISTS db_attribute_int04;")
        db.execute("DROP INDEX IF EXISTS db_attribute_int05;")
        db.execute("DROP INDEX IF EXISTS db_attribute_int06;")
        db.execute("DROP INDEX IF EXISTS db_attribute_int07;")

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
            'time01': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time02': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'varchar01': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'varchar02': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'varchar03': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'varchar04': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'varchar05': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
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
        'db.locationtype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'LocationType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_browsable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_significant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
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
            'left_city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'left_from_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'left_state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'db_index': 'True'}),
            'left_to_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'left_zip': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'postdir': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'predir': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'right_city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
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

    complete_apps = ['db']
