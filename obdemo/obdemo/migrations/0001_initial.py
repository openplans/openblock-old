# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ('streets', '0001_initial'),
        ('db', '0007_load_default_schemas'),
        )

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass


    models = {
        
    }

    complete_apps = ['obdemo']
