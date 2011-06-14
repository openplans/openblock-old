# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    # We tweak some of the default schemas for Boston.
    depends_on = (
        ("db", "0007_load_default_schemas"),
    )

    def forwards(self, orm):
        "rewritten as migration 0003, nothing left here."
        pass

    def backwards(self, orm):
        pass


    models = {
        
    }

    complete_apps = ['obdemo']
