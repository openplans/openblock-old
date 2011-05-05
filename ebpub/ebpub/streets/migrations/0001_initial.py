# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Block'
        db.create_table('blocks', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('predir', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('street_slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('street_pretty_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('suffix', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, blank=True)),
            ('postdir', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2, blank=True)),
            ('left_from_num', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('left_to_num', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('right_from_num', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('right_to_num', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('from_num', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('to_num', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('left_zip', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=10, null=True, blank=True)),
            ('right_zip', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=10, null=True, blank=True)),
            ('left_city', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('right_city', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('left_state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, db_index=True)),
            ('right_state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, db_index=True)),
            ('parent_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')()),
        ))
        db.send_create_signal('streets', ['Block'])

        # Adding model 'Street'
        db.create_table('streets', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('street_slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('suffix', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, db_index=True)),
        ))
        db.send_create_signal('streets', ['Street'])

        # Adding model 'Misspelling'
        db.create_table('streets_misspelling', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('incorrect', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('correct', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('streets', ['Misspelling'])

        # Adding model 'StreetMisspelling'
        db.create_table('streets_streetmisspelling', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('incorrect', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('correct', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('streets', ['StreetMisspelling'])

        # Adding model 'Place'
        db.create_table('streets_place', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('normalized_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('streets', ['Place'])

        # Adding model 'BlockIntersection'
        db.create_table('streets_blockintersection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['streets.Block'])),
            ('intersecting_block', self.gf('django.db.models.fields.related.ForeignKey')(related_name='intersecting_block', to=orm['streets.Block'])),
            ('intersection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['streets.Intersection'], null=True, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('streets', ['BlockIntersection'])

        # Adding unique constraint on 'BlockIntersection', fields ['block', 'intersecting_block']
        db.create_unique('streets_blockintersection', ['block_id', 'intersecting_block_id'])

        # Adding model 'Intersection'
        db.create_table('intersections', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64, db_index=True)),
            ('predir_a', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2, blank=True)),
            ('street_a', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('suffix_a', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, blank=True)),
            ('postdir_a', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2, blank=True)),
            ('predir_b', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2, blank=True)),
            ('street_b', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('suffix_b', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, blank=True)),
            ('postdir_b', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, db_index=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('streets', ['Intersection'])

        # Adding unique constraint on 'Intersection', fields ['predir_a', 'street_a', 'suffix_a', 'postdir_a', 'predir_b', 'street_b', 'suffix_b', 'postdir_b']
        db.create_unique('intersections', ['predir_a', 'street_a', 'suffix_a', 'postdir_a', 'predir_b', 'street_b', 'suffix_b', 'postdir_b'])

        # Adding model 'Suburb'
        db.create_table('streets_suburb', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('normalized_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('streets', ['Suburb'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Intersection', fields ['predir_a', 'street_a', 'suffix_a', 'postdir_a', 'predir_b', 'street_b', 'suffix_b', 'postdir_b']
        db.delete_unique('intersections', ['predir_a', 'street_a', 'suffix_a', 'postdir_a', 'predir_b', 'street_b', 'suffix_b', 'postdir_b'])

        # Removing unique constraint on 'BlockIntersection', fields ['block', 'intersecting_block']
        db.delete_unique('streets_blockintersection', ['block_id', 'intersecting_block_id'])

        # Deleting model 'Block'
        db.delete_table('blocks')

        # Deleting model 'Street'
        db.delete_table('streets')

        # Deleting model 'Misspelling'
        db.delete_table('streets_misspelling')

        # Deleting model 'StreetMisspelling'
        db.delete_table('streets_streetmisspelling')

        # Deleting model 'Place'
        db.delete_table('streets_place')

        # Deleting model 'BlockIntersection'
        db.delete_table('streets_blockintersection')

        # Deleting model 'Intersection'
        db.delete_table('intersections')

        # Deleting model 'Suburb'
        db.delete_table('streets_suburb')


    models = {
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
        'streets.blockintersection': {
            'Meta': {'ordering': "('block',)", 'unique_together': "(('block', 'intersecting_block'),)", 'object_name': 'BlockIntersection'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.Block']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intersecting_block': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'intersecting_block'", 'to': "orm['streets.Block']"}),
            'intersection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.Intersection']", 'null': 'True', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {})
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
        },
        'streets.misspelling': {
            'Meta': {'object_name': 'Misspelling'},
            'correct': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incorrect': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'streets.place': {
            'Meta': {'object_name': 'Place'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'normalized_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'streets.street': {
            'Meta': {'ordering': "('pretty_name',)", 'object_name': 'Street', 'db_table': "'streets'"},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'db_index': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'street_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'})
        },
        'streets.streetmisspelling': {
            'Meta': {'object_name': 'StreetMisspelling'},
            'correct': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incorrect': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'streets.suburb': {
            'Meta': {'object_name': 'Suburb'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'normalized_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['streets']
