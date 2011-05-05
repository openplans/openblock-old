# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Metro'
        db.create_table('metros_metro', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('short_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('metro_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('population', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('area', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('multiple_cities', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('state_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('location', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('metros', ['Metro'])

        # Adding unique constraint on 'Metro', fields ['name', 'state']
        db.create_unique('metros_metro', ['name', 'state'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Metro', fields ['name', 'state']
        db.delete_unique('metros_metro', ['name', 'state'])

        # Deleting model 'Metro'
        db.delete_table('metros_metro')


    models = {
        'metros.metro': {
            'Meta': {'unique_together': "(('name', 'state'),)", 'object_name': 'Metro'},
            'area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'metro_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'multiple_cities': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'population': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['metros']
