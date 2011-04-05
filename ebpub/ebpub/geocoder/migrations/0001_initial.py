# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GeocoderCache'
        db.create_table('geocoder_geocodercache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('normalized_location', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['streets.Block'], null=True, blank=True)),
            ('intersection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['streets.Intersection'], null=True, blank=True)),
            ('generated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('geocoder', ['GeocoderCache'])


    def backwards(self, orm):
        
        # Deleting model 'GeocoderCache'
        db.delete_table('geocoder_geocodercache')


    models = {
        'geocoder.geocodercache': {
            'Meta': {'object_name': 'GeocoderCache'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.Block']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'generated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intersection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.Intersection']", 'null': 'True', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'normalized_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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
        },
        'streets.intersection': {
            'Meta': {'ordering': "('slug',)", 'unique_together': "(('predir_a', 'street_a', 'suffix_a', 'postdir_a', 'predir_b', 'street_b', 'suffix_b', 'postdir_b'),)", 'object_name': 'Intersection', 'db_table': "'intersections'"},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'postdir_a': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'postdir_b': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'predir_a': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'predir_b': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'blank': 'True'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64', 'db_index': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'db_index': 'True'}),
            'street_a': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'street_b': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'suffix_a': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'suffix_b': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'})
        }
    }

    complete_apps = ['geocoder']
