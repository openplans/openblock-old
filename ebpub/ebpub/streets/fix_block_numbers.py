#!/usr/bin/env python
from django.conf import settings 
from ebpub.streets.name_utils import make_block_numbers
from ebpub.streets.models import Block

def update_block_numbers():
    Block.objects.exclude(right_city=settings.SHORT_NAME.upper()).exclude(left_city=settings.SHORT_NAME.upper()).delete()
    for b in Block.objects.all():
        (from_num, to_num) = make_block_numbers(b.left_from_num, 
        b.left_to_num, b.right_from_num, b.right_to_num)
        if b.from_num != from_num and b.to_num != to_num:
            b.from_num = from_num
            b.to_num = to_num
            b.save()

if __name__ == "__main__":
    update_block_numbers()
