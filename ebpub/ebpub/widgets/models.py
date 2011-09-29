from django.conf import settings
from django.contrib.gis.db import models
from ebpub.db.models import NewsItem, Location, Schema
import datetime
from operator import attrgetter

class TemplateManager(models.GeoManager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

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

    def natural_key(self):
        return (self.slug, )

    objects = TemplateManager()

    def __unicode__(self):
        return self.name


class WidgetManager(models.GeoManager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

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
    item_link_template = models.TextField(blank=True, null=True, help_text="If specified, this simple URL template is used to determine the url for items with openblock 'detail' pages, eg: 'http://mypublicsite.com/openblock/{{item.schema.name}}/{{item.id}}/'. For detailed information, see documentation.")

    #...
    
    def natural_key(self):
        return (self.slug, )

    objects = WidgetManager()
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.slug)

    @property
    def target_id(self):
        return "obw:%s" % self.slug

    def fetch_items(self, count=None, expire=True):
        """
        fetches items that should be displayed by 
        the widget.  This encorporates 'pinned' items
        and performs expiration on them.
        """
        if count is None:
            count = self.max_items
        
        widget_items = list(self.raw_item_query(count=count))
        now = datetime.datetime.now()
        
        # Iterate through any 'pinned' items for this 
        # widget.  Delete any that have expired.
        expired_pinned = []
        pinned_items = []
        for pi in PinnedItem.objects.filter(widget=self).all(): 
            # did it expire? 
            if pi.expiration_date is not None and pi.expiration_date < now:
                # get rid of it if so
                expired_pinned.append(pi)
            else: 
                pinned_items.append(pi)

        if expire:
            for pi in expired_pinned: 
                pi.delete()
        
        # If any of the pinned items are already in the list 
        # of items, remove them so that they will not appear 
        # twice.
        pinned_ids = set([pi.news_item.id for pi in pinned_items])
        widget_items = [x for x in widget_items if x.id not in pinned_ids]
        
        # Insert pinned items into the list of items
        pinned_items.sort(key=attrgetter('item_number'))
        for pi in pinned_items:
            widget_items.insert(pi.item_number, pi.news_item)
        
        return widget_items[:count]

    def raw_item_query(self, start=0, count=None):
        """
        gets items based on the filters set 
        on the widget. This does not include
        'pinned' items. 
        """
        # TODO integrate with other ways to search for items ?
        query = NewsItem.objects.all()
        
        type_filter = [x for x in self.types.all()]
        if len(type_filter): 
            query = query.filter(schema__in=type_filter)
        if self.location:
            query = query.filter(newsitemlocation__location=self.location)
        query = query.order_by('-item_date')
        
        if count is None: 
            count = self.max_items
        query = query[start:count]
        return query

    def embed_code(self):
        return '<div id="%s"></div><script src="http://%s/widgets/%s.js"></script>' % (self.target_id, settings.EB_DOMAIN, self.slug)
    
    def transclude_url(self):
        return "http://%s/widgets/%s" % (settings.EB_DOMAIN, self.slug)

class PinnedItem(models.Model):
    """
    represents an item that will be "pinned" in 
    a certain place in a widget (ie the 5th item
    regardless of what the query produces)
    """
    widget = models.ForeignKey(Widget)
    item_number = models.IntegerField()
    news_item = models.ForeignKey(NewsItem)
    expiration_date = models.DateTimeField(null=True)

