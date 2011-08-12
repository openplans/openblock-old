# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("streets", "0001_initial"),
    )



    def forwards(self, orm):
        
        # Adding model 'Schema'
        db.create_table('db_schema', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('plural_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('indefinite_article', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('min_date', self.gf('django.db.models.fields.DateField')()),
            ('last_updated', self.gf('django.db.models.fields.DateField')()),
            ('date_name', self.gf('django.db.models.fields.CharField')(default='Date', max_length=32)),
            ('date_name_plural', self.gf('django.db.models.fields.CharField')(default='Dates', max_length=32)),
            ('importance', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_special_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_collapse', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_newsitem_detail', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_charting', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uses_attributes_in_list', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('number_in_overview', self.gf('django.db.models.fields.SmallIntegerField')(default=5)),
            ('short_description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('summary', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('source', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('grab_bag_headline', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('grab_bag', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('short_source', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('update_frequency', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True)),
            ('intro', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('db', ['Schema'])

        # Adding model 'SchemaField'
        db.create_table('db_schemafield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('real_name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('pretty_name_plural', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('display', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_lookup', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_filter', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_charted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_order', self.gf('django.db.models.fields.SmallIntegerField')(default=10)),
            ('is_searchable', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('db', ['SchemaField'])

        # Adding unique constraint on 'SchemaField', fields ['schema', 'real_name']
        db.create_unique('db_schemafield', ['schema_id', 'real_name'])

        # Adding model 'LocationType'
        db.create_table('db_locationtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('plural_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('scope', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('is_browsable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_significant', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('db', ['LocationType'])

        # Adding model 'Location'
        db.create_table('db_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('normalized_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('location_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.LocationType'])),
            ('location', self.gf('django.contrib.gis.db.models.fields.GeometryField')(null=True)),
            ('centroid', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('area', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('population', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_mod_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('db', ['Location'])

        # Adding unique constraint on 'Location', fields ['slug', 'location_type']
        db.create_unique('db_location', ['slug', 'location_type_id'])

        # Adding model 'NewsItem'
        db.create_table('db_newsitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('item_date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.GeometryField')(null=True, blank=True)),
            ('location_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Location'], null=True, blank=True)),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['streets.Block'], null=True, blank=True)),
        ))
        db.send_create_signal('db', ['NewsItem'])

        # Adding model 'Attribute'
        db.create_table('db_attribute', (
            ('news_item', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['db.NewsItem'], unique=True, primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('varchar01', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('varchar02', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('varchar03', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('varchar04', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('varchar05', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('date01', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date02', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date03', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date04', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date05', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('time01', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('time02', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('datetime01', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('datetime02', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('datetime03', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('datetime04', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('bool01', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('bool02', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('bool03', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('bool04', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('bool05', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('int01', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('int02', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('int03', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('int04', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('int05', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('int06', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('int07', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('text01', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('db', ['Attribute'])

        # Adding model 'Lookup'
        db.create_table('db_lookup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema_field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.SchemaField'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('db', ['Lookup'])

        # Adding unique constraint on 'Lookup', fields ['slug', 'schema_field']
        db.create_unique('db_lookup', ['slug', 'schema_field_id'])

        # Adding model 'NewsItemLocation'
        db.create_table('db_newsitemlocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('news_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.NewsItem'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Location'])),
        ))
        db.send_create_signal('db', ['NewsItemLocation'])

        # Adding unique constraint on 'NewsItemLocation', fields ['news_item', 'location']
        db.create_unique('db_newsitemlocation', ['news_item_id', 'location_id'])

        # Adding model 'AggregateAll'
        db.create_table('db_aggregateall', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('db', ['AggregateAll'])

        # Adding model 'AggregateDay'
        db.create_table('db_aggregateday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
            ('date_part', self.gf('django.db.models.fields.DateField')(db_index=True)),
        ))
        db.send_create_signal('db', ['AggregateDay'])

        # Adding model 'AggregateLocation'
        db.create_table('db_aggregatelocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
            ('location_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.LocationType'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Location'])),
        ))
        db.send_create_signal('db', ['AggregateLocation'])

        # Adding model 'AggregateLocationDay'
        db.create_table('db_aggregatelocationday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
            ('location_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.LocationType'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Location'])),
            ('date_part', self.gf('django.db.models.fields.DateField')(db_index=True)),
        ))
        db.send_create_signal('db', ['AggregateLocationDay'])

        # Adding model 'AggregateFieldLookup'
        db.create_table('db_aggregatefieldlookup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
            ('schema_field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.SchemaField'])),
            ('lookup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Lookup'])),
        ))
        db.send_create_signal('db', ['AggregateFieldLookup'])

        # Adding model 'SearchSpecialCase'
        db.create_table('db_searchspecialcase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('redirect_to', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('db', ['SearchSpecialCase'])

        # Adding model 'DataUpdate'
        db.create_table('db_dataupdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('update_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('update_finish', self.gf('django.db.models.fields.DateTimeField')()),
            ('num_added', self.gf('django.db.models.fields.IntegerField')()),
            ('num_changed', self.gf('django.db.models.fields.IntegerField')()),
            ('num_deleted', self.gf('django.db.models.fields.IntegerField')()),
            ('num_skipped', self.gf('django.db.models.fields.IntegerField')()),
            ('got_error', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('db', ['DataUpdate'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'NewsItemLocation', fields ['news_item', 'location']
        db.delete_unique('db_newsitemlocation', ['news_item_id', 'location_id'])

        # Removing unique constraint on 'Lookup', fields ['slug', 'schema_field']
        db.delete_unique('db_lookup', ['slug', 'schema_field_id'])

        # Removing unique constraint on 'Location', fields ['slug', 'location_type']
        db.delete_unique('db_location', ['slug', 'location_type_id'])

        # Removing unique constraint on 'SchemaField', fields ['schema', 'real_name']
        db.delete_unique('db_schemafield', ['schema_id', 'real_name'])

        # Deleting model 'Schema'
        db.delete_table('db_schema')

        # Deleting model 'SchemaField'
        db.delete_table('db_schemafield')

        # Deleting model 'LocationType'
        db.delete_table('db_locationtype')

        # Deleting model 'Location'
        db.delete_table('db_location')

        # Deleting model 'NewsItem'
        db.delete_table('db_newsitem')

        # Deleting model 'Attribute'
        db.delete_table('db_attribute')

        # Deleting model 'Lookup'
        db.delete_table('db_lookup')

        # Deleting model 'NewsItemLocation'
        db.delete_table('db_newsitemlocation')

        # Deleting model 'AggregateAll'
        db.delete_table('db_aggregateall')

        # Deleting model 'AggregateDay'
        db.delete_table('db_aggregateday')

        # Deleting model 'AggregateLocation'
        db.delete_table('db_aggregatelocation')

        # Deleting model 'AggregateLocationDay'
        db.delete_table('db_aggregatelocationday')

        # Deleting model 'AggregateFieldLookup'
        db.delete_table('db_aggregatefieldlookup')

        # Deleting model 'SearchSpecialCase'
        db.delete_table('db_searchspecialcase')

        # Deleting model 'DataUpdate'
        db.delete_table('db_dataupdate')


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
