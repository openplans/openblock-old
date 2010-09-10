#!/usr/bin/env python
from django.conf import settings 
from ebpub.streets.name_utils import make_block_numbers
from ebpub.streets.models import Block


def update_all_block_numbers(verbose=False):
    """Derives from_num and to_num from left_from_num, etc.
    """
    not_in_city = Block.objects.exclude(right_city=settings.SHORT_NAME.upper()).exclude(left_city=settings.SHORT_NAME.upper())
    if verbose:
        print "Deleting %d blocks outside the city" % not_in_city.count()
    not_in_city.delete()
    for b in Block.objects.all():
        (from_num, to_num) = make_block_numbers(
            b.left_from_num, b.left_to_num, b.right_from_num, b.right_to_num)
        if b.from_num != from_num or b.to_num != to_num:
            b.from_num = from_num
            b.to_num = to_num
            b.save()
            if verbose:
                print "Updating numbers for %s to %s-%s" % (b, from_num, to_num)


if __name__ == "__main__":
    update_all_block_numbers(verbose=True)
