#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from operator import itemgetter
import re


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i1', '--input_file1', required=True)
  parser.add_argument('-i2', '--input_file2', required=True)
  parser.add_argument('-o', '--output_file', required=True)
  parser.add_argument('-m', '--mode', required=True)

  args = parser.parse_args()

  assert args.mode == 'v' or args.mode == 't'
  is_validation = args.mode == 'v'

  articles = defaultdict(list)
  for line in open(args.input_file1).read().splitlines():
    sentence = line.split()
    year = sentence[0]
    month = sentence[1]
    day = sentence[2]
    identifier = sentence[3]
    if is_validation:
      label = sentence[4]
      rest = sentence[5:]
      articles[(year, month, day, identifier, label)] = rest
    else:
      fold = sentence[4]
      label = sentence[5]
      rest = sentence[6:]
      articles[(year, month, day, identifier, fold, label)] = rest

  for line in open(args.input_file2).read().splitlines():
    sentence = line.split()
    year = sentence[0]
    month = sentence[1]
    day = sentence[2]
    identifier = sentence[3]
    if is_validation:
      label = sentence[4]
      rest = sentence[5:]
      articles[(year, month, day, identifier, label)].extend(rest)
    else:
      fold = sentence[4]
      label = sentence[5]
      rest = sentence[6:]
      articles[(year, month, day, identifier, fold, label)].extend(rest)

  of = open(args.output_file, 'w')
  for elem in articles:
    embeddings_as_str = ' '.join(str(e) for e in articles[elem])
    if is_validation:
      of.write('%s %s %s %s %s %s\n' % (elem[0], elem[1], elem[2], elem[3], elem[4], embeddings_as_str))
    else:
      of.write('%s %s %s %s %s %s %s\n' % (elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], embeddings_as_str))
  of.close()

if __name__ == '__main__':
  main()
