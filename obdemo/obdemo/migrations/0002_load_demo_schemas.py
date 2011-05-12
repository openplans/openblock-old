# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):


    def forwards(self, orm):
        from django.core.management import call_command
        call_command("loaddata", "boston_schemas.json")

    def backwards(self, orm):
        "Write your backwards methods here."
        # We can't safely remove the demo schemas because users may
        # have hand-modified them, added new ones, etc.
        pass


    models = {
        
    }

    complete_apps = ['obdemo']
