from django.utils.simplejson import JSONEncoder
from bunch import Bunch # relative import

class ClusterJSON(JSONEncoder):
    """Format Bunches as [[list of object IDs], [center x, center y]]
    """
    def default(self, o):
        if isinstance(o, Bunch):
            return [o.objects, o.center]
        else:
            return JSONEncoder.default(self, o)
