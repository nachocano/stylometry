#!/usr/bin/python
from __future__ import division
import argparse
import numpy as np
from collections import defaultdict

def read_lines(f):
    for ii,line in enumerate(f):
        yield line

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--input_file', required=True)
  args = parser.parse_args()

  s = set()
  counter = 0
  for line in read_lines(open(args.input_file, 'r')):
    print 'processing %s' % counter 
    counter +=1
    splitted = line.split()
    did, gid, _, _ = splitted[0].split("_")
    for l in splitted[1:]:
      v = '%s_%s_%s' % (l, did, gid)
      if v in s:
        print '%s already in s' % v
      s.add(v)
  print '%s unique stuff' % len(s)

if __name__ == '__main__':
  main()

