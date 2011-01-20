from django.contrib.gis.db import models
from django.db import connection, transaction

def field_mapping(schema_id_list):
    """
    Given a list of schema IDs, returns a dictionary of dictionaries, mapping
    schema_ids to dictionaries mapping the fields' name->real_name.
    Example return value:
        {1: {u'crime_type': 'varchar01', u'crime_date', 'date01'},
         2: {u'permit_number': 'varchar01', 'to_date': 'date01'},
        }
    """
    # schema_fields = [{'schema_id': 1, 'name': u'crime_type', 'real_name': u'varchar01'},
    #                  {'schema_id': 1, 'name': u'crime_date', 'real_name': u'date01'}]
    from ebpub.db.models import SchemaField
    result = {}
    for sf in SchemaField.objects.filter(schema__id__in=(schema_id_list)).values('schema', 'name', 'real_name'):
        result.setdefault(sf['schema'], {})[sf['name']] = sf['real_name']
    return result


class AttributesDescriptor(object):  # XXX THIS CAN DIE
    """
    This class provides the functionality that makes the attributes available
    as `attributes` on a model instance.
    """
    def __get__(self, instance, instance_type=None):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self.__class__.__name__)
        if not hasattr(instance, '_attributes_cache'):
            select_dict = field_mapping([instance.schema_id])[instance.schema_id]
            instance._attributes_cache = AttributeDict(instance.id, instance.schema_id, select_dict)
        return instance._attributes_cache

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self.__class__.__name__)
        if not isinstance(value, dict):
            raise ValueError('Only a dictionary is allowed')
        mapping = field_mapping([instance.schema_id])[instance.schema_id].items()
        values = [value.get(k, None) for k, v in mapping]
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE %s
            SET %s
            WHERE news_item_id = %%s
            """ % (Attribute._meta.db_table, ','.join(['%s=%%s' % v for k, v in mapping])),
                values + [instance.id])
        # If no records were updated, that means the DB doesn't yet have a
        # row in the attributes table for this news item. Do an INSERT.
        if cursor.rowcount < 1:
            cursor.execute("""
                INSERT INTO %s (news_item_id, schema_id, %s)
                VALUES (%%s, %%s, %s)""" % (Attribute._meta.db_table, ','.join([v for k, v in mapping]), ','.join(['%s' for k in mapping])),
                [instance.id, instance.schema_id] + values)
        transaction.commit_unless_managed()


class AttributeDict(dict):  # XXX THIS CAN DIE
    """
    A dictionary-like object that serves as a wrapper around attributes for a
    given NewsItem.
    """
    def __init__(self, news_item_id, schema_id, mapping):
        dict.__init__(self)
        self.news_item_id = news_item_id
        self.schema_id = schema_id
        self.mapping = mapping # name -> real_name dictionary
        self.cached = False

    def __do_query(self):
        if not self.cached:
            attr_values = Attribute.objects.filter(news_item__id=self.news_item_id).extra(select=self.mapping).values(*self.mapping.keys())
            # Rarely, we might have added the first SchemaField for this
            # Schema *after* the NewsItem was scraped.  In that case
            # attr_values will be empty list.
            if attr_values:
                self.update(attr_values[0])
            self.cached = True

    def get(self, *args, **kwargs):
        self.__do_query()
        return dict.get(self, *args, **kwargs)

    def __getitem__(self, name):
        self.__do_query()
        return dict.__getitem__(self, name)

    def __setitem__(self, name, value):
        # TODO: refactor, code overlaps largely with AttributeDescriptor.__set__
        cursor = connection.cursor()
        real_name = self.mapping[name]
        cursor.execute("""
            UPDATE %s
            SET %s = %%s
            WHERE news_item_id = %%s
            """ % (Attribute._meta.db_table, real_name), [value, self.news_item_id])
        # If no records were updated, that means the DB doesn't yet have a
        # row in the attributes table for this news item. Do an INSERT.
        if cursor.rowcount < 1:
            cursor.execute("""
                INSERT INTO %s (news_item_id, schema_id, %s)
                VALUES (%%s, %%s, %%s)""" % (Attribute._meta.db_table, real_name),
                [self.news_item_id, self.schema_id, value])
        transaction.commit_unless_managed()
        dict.__setitem__(self, name, value)

class Attribute(models.Model): #XXX THIS CAN DIE
    """
    Extended metadata for NewsItems.

    Each row contains all the extra metadata for one NewsItem
    instance.  The field names are generic, so in order to know what
    they mean, you must look at the SchemaFields for the Schema for
    that NewsItem.  eg. newsitem.

    """
    news_item = models.ForeignKey('db.NewsItem', primary_key=True, unique=True)
    schema = models.ForeignKey('db.Schema')
    # All data-type field names must end in two digits, because the code assumes this.
    varchar01 = models.CharField(max_length=255, blank=True, null=True)
    varchar02 = models.CharField(max_length=255, blank=True, null=True)
    varchar03 = models.CharField(max_length=255, blank=True, null=True)
    varchar04 = models.CharField(max_length=255, blank=True, null=True)
    varchar05 = models.CharField(max_length=255, blank=True, null=True)
    date01 = models.DateField(blank=True, null=True)
    date02 = models.DateField(blank=True, null=True)
    date03 = models.DateField(blank=True, null=True)
    date04 = models.DateField(blank=True, null=True)
    date05 = models.DateField(blank=True, null=True)
    time01 = models.TimeField(blank=True, null=True)
    time02 = models.TimeField(blank=True, null=True)
    datetime01 = models.DateTimeField(blank=True, null=True)
    datetime02 = models.DateTimeField(blank=True, null=True)
    datetime03 = models.DateTimeField(blank=True, null=True)
    datetime04 = models.DateTimeField(blank=True, null=True)
    bool01 = models.NullBooleanField(blank=True)
    bool02 = models.NullBooleanField(blank=True)
    bool03 = models.NullBooleanField(blank=True)
    bool04 = models.NullBooleanField(blank=True)
    bool05 = models.NullBooleanField(blank=True)
    int01 = models.IntegerField(blank=True, null=True)
    int02 = models.IntegerField(blank=True, null=True)
    int03 = models.IntegerField(blank=True, null=True)
    int04 = models.IntegerField(blank=True, null=True)
    int05 = models.IntegerField(blank=True, null=True)
    int06 = models.IntegerField(blank=True, null=True)
    int07 = models.IntegerField(blank=True, null=True)
    text01 = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'Attributes for news item %s' % self.news_item_id
