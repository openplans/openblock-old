# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("db", "0014__undo_0009"),
    )

    def forwards(self, orm):
        from django.core.management import call_command
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        call_command("loaddata", os.path.join(here, "0004_more_schemas.json"))

    def backwards(self, orm):
        pass

    models = {
    }

    complete_apps = ['obdemo']
