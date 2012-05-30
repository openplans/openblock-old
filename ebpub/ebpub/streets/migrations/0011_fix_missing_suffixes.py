# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
import re

class Migration(DataMigration):

    def forwards(self, orm):
        # Clean up streets that had the suffix stuffed into the name,
        # due to bad census data.
        # This happened a lot with streets ending in 'PARK',
        # eg. {street='WILSON PARK', suffix=''}
        # should be fixed as {street='WILSON', suffix='PARK'}.
        # As a result, nothing on those streets could be geocoded properly.
        # And this propagated to Blocks and Intersections as well :(
        try:
            from ebpub.geocoder.parser import parsing
            suffix_standardizer = parsing.STANDARDIZERS['suffix']
            suffix_matcher = parsing.TOKEN_REGEXES['suffix']
        except (ImportError, NameError, KeyError):
            print "Can't fix data, we depend on ebpub.geocoder.parser.parsing code that's apparently not there anymore!"
            return

        def smart_title(s, exceptions=None):
            # Copied from ebpub.utils.text
            result = re.sub(r"(?<=[\s\"\(-])(\w)", lambda m: m.group(1).upper(), s.lower())
            if result:
                result = result[0].upper() + result[1:]

            # Handle the exceptions.
            if exceptions is not None:
                for e in exceptions:
                    pat = re.escape(e)
                    if re.search("^\w", pat):
                        pat = r"\b%s" % pat
                    if re.search("\w$", pat):
                        pat = r"%s\b" % pat
                    pat = r"(?i)%s" % pat
                    result = re.sub(pat, e, result)

            return result


        def make_street_pretty_name(street, suffix):
            # Copied from ebpub.streets.name_utils.
            street_name = smart_title(street)
            if suffix:
                street_name += u' %s.' % smart_title(suffix)
            return street_name

        lacking_suffixes = orm['streets.street'].objects.filter(suffix='')
        for street in lacking_suffixes:
            if street.street.count(' '):
                old_norm_name = street.street
                name_parts = street.pretty_name.upper().split()
                raw_suffix = name_parts.pop().upper()
                name = ' '.join(name_parts)
                # Check if it's a known suffix.
                if suffix_matcher.match(raw_suffix):
                    street.suffix = suffix = suffix_standardizer(raw_suffix)
                    street.street = name
                    street.pretty_name = make_street_pretty_name(name, suffix)
                    # Dicey: assume that the standardizer gave us back
                    # something like 'PARK' rather than 'ST', and so
                    # doesn't need a trailing dot for the pretty name.
                    street.pretty_name = street.pretty_name.rstrip('.')
                    street.save()
                    print "Fixed street %s" % street.pretty_name
                    # Ugh, fix intersections too.
                    # Assume their pretty_name & slug are already OK.
                    for intersection in orm['streets.intersection'].objects.filter(
                          street_a=old_norm_name, suffix_a=''):
                        intersection.street_a = street.street
                        intersection.suffix_a = street.suffix
                        intersection.save()
                        print "Fixed intersection %s" % intersection.pretty_name
                    for intersection in orm['streets.intersection'].objects.filter(
                          street_b=old_norm_name, suffix_b=''):
                        intersection.street_b = street.street
                        intersection.suffix_b = street.suffix
                        try:
                            intersection.save()
                        except:
                            raise

                        print "Fixed intersection %s" % intersection.pretty_name
                    # And fix blocks too. Whee.
                    for block in orm['streets.block'].objects.filter(
                        street=old_norm_name):
                        block.street = street.street
                        block.suffix = street.suffix
                        block.save()
                        print "Fixed block %s" % block.pretty_name

    def backwards(self, orm):
        "Write your backwards methods here."
        pass


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
