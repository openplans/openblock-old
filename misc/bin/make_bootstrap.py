#!/usr/bin/env python

if __name__ == '__main__':
    import sys
    import virtualenv

    if len(sys.argv) < 3: 
        print 'usage: %s <in> <out>'
        sys.exit(0)

    in_file = sys.argv[1]
    out_file = sys.argv[2]

    extras = open(in_file).read()
    output = virtualenv.create_bootstrap_script(open(in_file).read())
    f = open(out_file, 'w').write(output)
