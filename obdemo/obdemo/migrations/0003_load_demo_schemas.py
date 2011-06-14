# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("db", "0011_delete_schemafield_name"),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        from django.core.management import call_command
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        call_command("loaddata", os.path.join(here, "0003_boston_schemas.json"))

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
    }

    complete_apps = ['obdemo']
