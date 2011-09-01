from django.contrib.gis.db import models
from ebpub.accounts.models import User
from ebpub.db.models import NewsItem

class NewsItemCreator(models.Model):
    """
    represents an add-on created-by relationship between 
    a User and a NewsItem without interfering with the 
    NewsItem model.
    """

    news_item = models.ForeignKey(NewsItem)    
    user = models.ForeignKey(User)
    
    class Meta:
        unique_together = (('news_item', 'user'),)
        ordering = ('news_item',)
    

    
