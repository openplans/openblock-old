#!/usr/bin/env python
from django.conf import settings
from ebpub.streets.models import Block


def delete_blocks_outside_city(verbose=False):
    """Derives from_num and to_num from left_from_num, etc.
    """
    not_in_city = Block.objects.exclude(right_city=settings.SHORT_NAME.upper()).exclude(left_city=settings.SHORT_NAME.upper())
    if verbose:
        print "Deleting %d blocks outside the city" % not_in_city.count()
    not_in_city.delete()


if __name__ == "__main__":
    delete_blocks_outside_city(verbose=True)
