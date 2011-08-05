from django.conf import settings
from django.contrib.gis.db import models
from ebpub.db.models import NewsItem, Location, Schema

# Create your models here.

class Template(models.Model):
    """
    django template stored in the database
    representing the html output of a widget.
    """
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    code = models.TextField(blank=True)
    content_type = models.CharField(max_length=128, default='text/html')

    def __unicode__(self):
        return self.name


class Widget(models.Model):
    """
    """
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    template = models.ForeignKey(Template)
    max_items = models.IntegerField(default=10)
    types = models.ManyToManyField(Schema, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True)
    item_link_template = models.TextField(blank=True, null=True, help_text="If specified, this simple URL template is used to determine the url for items with openblock 'detail' pages, eg: 'http://mypublicsite.com/openblock/{{schema.name}}/{{id}}/'. For detailed information, see documentation.")

    #...
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.slug)

    @property
    def target_id(self):
        return "obw:%s" % self.slug

    def fetch_items(self):
        return self._item_query()

    def _item_query(self):
        # TODO integrate with other ways to search for items ?
        query = NewsItem.objects.all()
        
        type_filter = [x for x in self.types.all()]
        if len(type_filter): 
            query = query.filter(schema__in=type_filter)
        if self.location:
            query = query.filter(newsitemlocation__location=self.location)
        query = query.order_by('-item_date')
        query = query[:self.max_items]
        return query

    def embed_code(self):
        return '<div id="%s"></div><script src="http://%s/widgets/%s.js"></script>' % (self.target_id, settings.EB_DOMAIN, self.slug)
    
    def transclude_url(self):
        return "http://%s/widgets/%s" % (settings.EB_DOMAIN, self.slug)

# class PinnedItem(models.Model):
#     """
#     """
#     item_number = models.IntegerField()
#     news_item = models.ForeignKey(NewsItem)
#     widget = models.ForeignKey(Widget)

# class BannedItem(models.Model):
#     """
#     """
#     item_number = models.IntegerField()
#     news_item = models.ForeignKey(NewsItem)
#     widget = models.ForeignKey(Widget)

