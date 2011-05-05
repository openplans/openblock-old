# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
            ("db", "0001_initial"),
            ("streets", "0001_initial")
        )

    def forwards(self, orm):

        # Adding model 'Seed'
        db.create_table('blobs_seed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('base_url', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('delay', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('depth', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('is_crawled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_rss_feed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rss_full_entry', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('normalize_www', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['db.Schema'])),
            ('autodetect_locations', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('guess_article_text', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('strip_noise', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal('blobs', ['Seed'])

        # Adding model 'Page'
        db.create_table('blobs_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('seed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blobs.Seed'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=512, db_index=True)),
            ('scraped_url', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('when_crawled', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_article', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('is_pdf', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_printer_friendly', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('article_headline', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('article_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('has_addresses', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('when_geocoded', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('geocoded_by', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('times_skipped', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('robot_report', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('blobs', ['Page'])

        # Adding model 'IgnoredDateline'
        db.create_table('blobs_ignoreddateline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dateline', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('blobs', ['IgnoredDateline'])


    def backwards(self, orm):
        
        # Deleting model 'Seed'
        db.delete_table('blobs_seed')

        # Deleting model 'Page'
        db.delete_table('blobs_page')

        # Deleting model 'IgnoredDateline'
        db.delete_table('blobs_ignoreddateline')


    models = {
        'blobs.ignoreddateline': {
            'Meta': {'object_name': 'IgnoredDateline'},
            'dateline': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'blobs.page': {
            'Meta': {'object_name': 'Page'},
            'article_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'article_headline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geocoded_by': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'has_addresses': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_article': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_pdf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_printer_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'robot_report': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'scraped_url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'seed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blobs.Seed']"}),
            'times_skipped': ('django.db.models.fields.SmallIntegerField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'when_crawled': ('django.db.models.fields.DateTimeField', [], {}),
            'when_geocoded': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'blobs.seed': {
            'Meta': {'object_name': 'Seed'},
            'autodetect_locations': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'base_url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'delay': ('django.db.models.fields.SmallIntegerField', [], {}),
            'depth': ('django.db.models.fields.SmallIntegerField', [], {}),
            'guess_article_text': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_crawled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_rss_feed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'normalize_www': ('django.db.models.fields.SmallIntegerField', [], {}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rss_full_entry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['db.Schema']"}),
            'strip_noise': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '512'})
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
        }
    }

    complete_apps = ['blobs']
