import argparse
from collections import defaultdict
from collections import Counter, OrderedDict


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--idx_input_file', required=True) # ixs input file
  parser.add_argument('-o', '--idx_output_file', required=True) #] idx output file
  args = parser.parse_args()

  of = open(args.idx_output_file, 'w')
  for line in open(args.idx_input_file).read().splitlines():
    doc = line.split()
    did, gid, fid, label = doc[0], doc[1], doc[2], doc[3]
    rest = doc[4:]
    #print len(rest)
    mid = len(rest)/2
    print mid
    rest1_as_str = ' '.join([str(i) for i in rest[:mid]])
    rest2_as_str = ' '.join([str(i) for i in rest[mid:]])
    of.write('%s %s %s %s %s\n' % (did, gid, fid, label, rest1_as_str))
    of.write('%s %s %s %s %s\n' % (did, gid, fid, label, rest2_as_str))

if __name__ == '__main__':
  main()  