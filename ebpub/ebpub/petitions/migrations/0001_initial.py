# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Petition'
        db.create_table('petitions_petition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'], null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, blank=True)),
            ('data_name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('teaser', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('petition', self.gf('django.db.models.fields.TextField')()),
            ('creation_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('petitions', ['Petition'])

        # Adding model 'Petitioner'
        db.create_table('petitions_petitioner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('petition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['petitions.Petition'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('notes', self.gf('django.db.models.fields.TextField')()),
            ('date_signed', self.gf('django.db.models.fields.DateTimeField')()),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('petitions', ['Petitioner'])


    def backwards(self, orm):
        
        # Deleting model 'Petition'
        db.delete_table('petitions_petition')

        # Deleting model 'Petitioner'
        db.delete_table('petitions_petitioner')


    models = {
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
        'petitions.petition': {
            'Meta': {'object_name': 'Petition'},
            'creation_date': ('django.db.models.fields.DateField', [], {}),
            'data_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'petition': ('django.db.models.fields.TextField', [], {}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'teaser': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'petitions.petitioner': {
            'Meta': {'object_name': 'Petitioner'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'date_signed': ('django.db.models.fields.DateTimeField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'petition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['petitions.Petition']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['petitions']
