#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from operator import itemgetter
import re


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i1', '--input_file1', required=True)
  parser.add_argument('-i2', '--input_file2', require=True)
  parser.add_argument('-o', '--output_file', required=True)
  args = parser.parse_args()

  books = defaultdict(list)
  for line in open(args.input_file1).read().splitlines():
    sentence = line.split()
    did = sentence[0]
    gid = sentence[1]
    fid = sentence[2]
    label = sentence[3]
    rest = sentence[4:]
    books[(did, gid, fid, label)] = rest

  for line in open(args.input_file2).read().splitlines():
    sentence = line.split()
    did = sentence[0]
    gid = sentence[1]
    fid = sentence[2]
    label = sentence[3]
    rest = sentence[4:]
    books[(did, gid, fid, label)].extend(rest)

  of = open(args.output_file, 'w')
  for elem in books:
    embeddings_as_str = ' '.join(str(e) for e in books[elem])
    of.write('%s %s %s %s %s\n' % (elem[0], elem[1], elem[2], elem[3], embeddings_as_str))
  of.close()

if __name__ == '__main__':
  main()
