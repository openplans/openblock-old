from ebgeo.utils import clustering

def cluster_newsitems(qs, radius=26):
    """
    A convenience function for clustering a newsitem queryset.

    Returns: a mapping of scale -> list of clusters for that scale.
    """
    return clustering.cluster_scales(
        dict([(ni.id, (ni.location.centroid.x, ni.location.centroid.y))
              for ni in qs if ni.location]),
        radius)
