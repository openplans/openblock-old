# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'PlaceType.map_icon_url'
        db.add_column('streets_placetype', 'map_icon_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'PlaceType.map_color'
        db.add_column('streets_placetype', 'map_color', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        import tempfile, os, sys
        sys.stderr.write("WARNING, destroying PlaceType.map_icon_url column\n")
        sys.stderr.write("WARNING, destroying PlaceType.map_color column\n")
        # Want to dump a fixture here.  Can't just use
        # call_command('dumpdata') because it knows about *current*
        # model code, not South's own ORM state.
        tmpdir = tempfile.mkdtemp()
        tmpname = os.path.join(tmpdir, 'placetypes_icons_colors.json')
        sys.stderr.write("... will try to save data in %s\n" % tmpname)
        try:
            dumpfile = open(tmpname, 'w')
            ptypes = orm.PlaceType.objects.all()
            from django.core import serializers
            serializer = serializers.get_serializer('json')()
            serializer.serialize(ptypes, stream=dumpfile)
            sys.stderr.write("\n... saved\n")
        except Exception, e:
            sys.stderr.write("\n... failed to save data:\n%s\n" % e)

        # Deleting field 'PlaceType.map_icon_url'
        db.delete_column('streets_placetype', 'map_icon_url')

        # Deleting field 'PlaceType.map_color'
        db.delete_column('streets_placetype', 'map_color')


    models = {
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
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'blank': 'True'}),
            'normalized_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'place_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.PlaceType']"}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'streets.placesynonym': {
            'Meta': {'object_name': 'PlaceSynonym'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'normalized_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['streets.Place']"}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'streets.placetype': {
            'Meta': {'object_name': 'PlaceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indefinite_article': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'is_geocodable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_mappable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'map_color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'map_icon_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'plural_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
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
