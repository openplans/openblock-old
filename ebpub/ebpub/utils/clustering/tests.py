# TODO: turn these into proper unit tests.

"""
Tests for developing map marker clustering module
"""

import random
from ebpub.utils.clustering import cluster_by_scale, cluster_scales
from ebpub.utils.clustering import cluster
from ebpub.utils.clustering import sample
from ebpub.utils.clustering import json

def gen_test_points(n=50, extent=(0,0,100,100), rand_seed=None):
    """
    Returns a list of n (x, y) pairs, distributed randomly throughout the extent.
    """
    if rand_seed:
        random.seed(rand_seed)
    return [(random.randint(extent[0], extent[2]), random.randint(extent[1], extent[3]))
            for i in xrange(n)]

def gen_test_objs(n=50, extent=(0,0,100,100), rand_seed=None):
    """
    Returns a mapping of id -> (x, y), where id is an int.
    """
    points = gen_test_points(n=n, extent=extent, rand_seed=rand_seed)
    return dict(zip(xrange(len(points)), points))

def print_bunches(bunches, *args, **kwargs):
    for i, bunch in enumerate(bunches):
        print "%3d: %d objects" % (i+1, len(bunch.objects))

def plot_bunches(bunches, buffer):
    import pylab
    from matplotlib.patches import Circle
    # Plot points
    points = []
    for b in bunches:
        points.extend(b.points)
        # or maybe: points.append(b.center)
    pylab.plot([p[0] for p in points], [p[1] for p in points], 'r+')
    subplot = pylab.figure(1).axes[0]
    # Plot clusters
    for b in bunches:
        e = Circle((b.x, b.y), buffer, facecolor="green", alpha=0.4)
        subplot.add_artist(e)
    pylab.show()

def display(bunches, buffer, f=plot_bunches):
    f(bunches, buffer)

def timeit(label, f, *args, **kwargs):
    import time, sys
    start = time.time()
    ret_val = f(*args, **kwargs)
    print >> sys.stderr, "%s took %.4f seconds" % (label, time.time()-start)
    return ret_val

def randomize(L):
    import copy, random
    Lprime = copy.copy(L)
    random.shuffle(Lprime)
    return Lprime

def main():
    buffer = 20
    objs = gen_test_objs(rand_seed="foo")
    bunches = timeit("cluster", cluster.buffer_cluster, objs, buffer)
    display(bunches, buffer=buffer, f=print_bunches)

if __name__ == "__main__":
    print "main:"
    main()
    print "cluster_by_scale:"
    for bunch in cluster_by_scale(sample.sample_pts, 51, 19200):
        print "%3d objects: center (%.4f, %.4f)" % (len(bunch.objects), bunch.x, bunch.y)
    print "cluster_scales:"
    clusters_by_scale = cluster_scales(sample.sample_pts, 26)
    from django.utils.simplejson import dumps
    print dumps(clusters_by_scale, cls=json.ClusterJSON,
                sort_keys=True, indent=2)
    #import pprint
    #pprint.pprint(clusters_by_scale)
