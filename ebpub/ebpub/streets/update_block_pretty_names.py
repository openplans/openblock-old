#!/usr/bin/env python
from ebpub.streets.name_utils import make_pretty_name
from ebpub.streets.models import Block

def update_block_pretty_names():
    for b in Block.objects.all():
        #name = make_pretty_name(b.from_num, b.to_num, b.predir, b.street, b.suffix)[1]
        name = make_pretty_name(b.left_from_num, b.left_to_num, 
        b.right_from_num, b.right_to_num, b.predir, b.street, b.suffix, 
        b.postdir)[1]
        if name != b.pretty_name:
            print '%s -- %s' % (b.pretty_name, name)
            b.pretty_name = name
            b.save()

if __name__ == "__main__":
    update_block_pretty_names()



