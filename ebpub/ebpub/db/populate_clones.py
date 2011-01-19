from django.db import transaction
from ebpub.db import models

def populate_new_from_old_all(delete=False):
    for model in (models.TestyIssuesModel,):
        print "Deleting all existing of new model %s" % (model.schemaslug,)
        model.objects.all().delete()
        print "Populating new model %s" % (model.schemaslug,)
        populate_one_new_from_old(model, delete=delete)

def populate_one_new_from_old(model, delete=False):
    """
    Populate the given model by cloning instances of old-school NewsItem that
    have the schema designated by model.schemaslug
    """
    items = list(models.NewsItem.objects.filter(schema__slug=model.schemaslug))
    for i, item in enumerate(items):
        new_item = model(schema=item.schema, title='NEW MODEL ' + item.title,
                         description=item.description, url=item.url,
                         pub_date=item.pub_date, item_date=item.item_date,
                         location=item.location,
                         location_name=item.location_name,
                         location_object=item.location_object,
                         block=item.block)
        # Trick to get the attributes to load. Bizarrely I don't know how
        # else to force this!
        item.attributes.get('pasiodufipoasufoisaufopias')

        # if item.attributes.get('rating') is None:
        #     if delete:
        #         print "oops, got a new one? deleting %s" % item.title
        #         item.delete()
        #         continue

        # Need a pk before we can do many-to-many.
        new_item.save()

        if len(item.attributes):
            for sf in item.schema.schemafield_set.all():
                val = item.attributes[sf.name]
                key = sf.name
                if sf.is_lookup:
                    key = key + '_id'
                    if sf.is_many_to_many_lookup():
                        val = map(int, val.split(','))
                setattr(new_item, key, val)

            new_item.save()

    print "Saved %d new %ss" % (i + 1, model.schemaslug)
    if delete:
        print "Deleting old ones"
        for item in items:
            item.delete()
        # Or by hand:
        # delete from db_attribute where schema_id = 5 and news_item_id not in (select newsitem_ptr_id from db_testyissuesmodel);
        # delete from db_newsitem where schema_id = 5 and id not in (select newsitem_ptr_id from db_testyissuesmodel);


def populate_old_model_from_new(model, clone=False, delete=False):
    """
    Populate old-school NewsItems with Attributes by either just making
    and linking to an Attributes instance if clone==False,
    or cloning full instances of the new-school `model` if clone==True.

    If delete==True, instances of new-school model will be deleted too.
    """
    items = list(model.objects.all())
    parent_model = models.NewsItem
    for i, item in enumerate(items):
        if clone:

            new_item = parent_model(
                             schema=item.schema, title='NEW MODEL ' + item.title,
                             description=item.description, url=item.url,
                             pub_date=item.pub_date, item_date=item.item_date,
                             location=item.location,
                             location_name=item.location_name,
                             location_object=item.location_object,
                             block=item.block)
            new_item.save()
            print "Creating old-style clone %s" % new_item
        else:
            new_item = item.newsitem_ptr
            print "Saving old-style attributes for %s" % new_item
        if len(item.attributes):
            attrs = dict(item.attributes)
            for sf in item.schema.schemafield_set.all():
                val = attrs[sf.name]
                key = sf.name
                if sf.is_many_to_many_lookup():
                    val = ','.join([str(s.id) for s in val.all()])
                elif sf.is_lookup:
                    val = val.all()
                    if val:
                        val = val[0].id
                    else:
                        val = None
                attrs[key] = val
            new_item.attributes = attrs

    print "Saved %d NewsItems" % (i + 1)
    if delete:
        model.objects.all().delete()
