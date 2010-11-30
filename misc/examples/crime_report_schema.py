#
# This code creates a custom news item Schema, 
# custom attributes and a NewsItem of the 
# type.  For a narrative description, see 
# The accompanying documentation in docs/schema.rst
#

from ebpub.db.models import Schema, SchemaField, NewsItem
from datetime import datetime

if __name__ == '__main__':
    # create schema
    crime_report = Schema()
    crime_report.indefinite_article = 'a'
    crime_report.name = "Crime Report"
    crime_report.plural_name = "Crime Reports"
    crime_report.slug = 'crimereport'
    crime_report.min_date = datetime.utcnow()
    crime_report.last_updated = datetime.utcnow()
    crime_report.has_newsitem_detail = True
    crime_report.is_public = True
    crime_report.save()

    # custom field officer name 
    officer = SchemaField()
    officer.schema = crime_report
    officer.pretty_name = "Reporting Officer's Name"
    officer.pretty_name_plural = "Reporting Officer's Names"
    officer.real_name = 'varchar01'
    officer.name = 'officer'
    officer.save()

    # custom field crime type 
    crime_name = SchemaField()
    crime_name.schema = crime_report
    crime_name.pretty_name = "Crime Type"
    crime_name.pretty_plural_name = "Crime Types"
    crime_name.real_name = "varchar02"
    crime_name.name = "crime_type"
    crime_name.save()

    # custom field crime code
    crime_code = SchemaField()
    crime_code.schema = crime_report
    crime_code.pretty_name = "Crime Code"
    crime_code.pretty_plural_name = "Crime Codes"
    crime_code.real_name = "int01"
    crime_code.name = "crime_code"
    crime_code.save()

    # create a Crime Report!
    report = NewsItem()
    report.schema = crime_report
    report.title = "Hooligans causing disturbance downtown"
    report.location_name = "123 Fakey St."
    report.item_date = datetime.utcnow()
    report.pub_date = datetime.utcnow()
    report.description = "Blah Blah Blah"
    report.save()
    report.attributes['officer'] = "John Smith"
    report.attributes['crime_type'] = "Disturbing The Peace"
    report.attributes['crime_code'] = 187
