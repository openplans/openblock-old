#!/usr/bin/env python
from ebpub.streets.name_utils import make_block_numbers
from ebpub.streets.models import Block


def update_all_block_numbers(verbose=False):
    """Derives from_num and to_num from left_from_num, etc.
    """
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
