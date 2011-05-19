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
        from django.core.management import call_command
        call_command("loaddata", "boston_schemas.json")
        call_command(
            "loaddata",
            "ebdata/ebdata/scrapers/us/ma/boston/businesses/business_licences_schema")
        call_command(
            "loaddata",
            "ebdata/ebdata/scrapers/us/ma/boston/restaurants/restaurant_inspection_schema")
        call_command(
            "loaddata",
            "ebdata/ebdata/scrapers/us/ma/boston/building_permits/building_permit_schema")
        call_command(
            "loaddata",
            "ebdata/ebdata/scrapers/us/ma/boston/police_reports/police_report_schema")

    def backwards(self, orm):
        "Write your backwards methods here."
        # We can't safely remove the demo schemas because users may
        # have hand-modified them, added new ones, etc.
        pass


    models = {
        
    }

    complete_apps = ['obdemo']
