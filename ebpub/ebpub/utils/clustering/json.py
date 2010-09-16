from django.utils.simplejson import JSONEncoder
# not to be confused with ebpub.utils.bunch of course...
from ebpub.utils.clustering.bunch import Bunch 

class ClusterJSON(JSONEncoder):
    """Format Bunches as [[list of object IDs], [center x, center y]]
    """
    def default(self, o):
        if isinstance(o, Bunch):
            return [o.objects, o.center]
        else:
            return JSONEncoder.default(self, o)
