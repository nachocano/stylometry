#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from operator import itemgetter
import re

# 35152 max sentence
# 15236 max words in a sentence
def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--input_file', required=True)
  args = parser.parse_args()

  greatest = 0
  best_line = None
  for line in open(args.input_file).read().splitlines():
    line_splitted = line.split()
    if len(line_splitted) > greatest:
      greatest = len(line_splitted)
      best_line = line
  print 'biggest novel has %s sentences' % greatest
  #print 'line %s' % best_line

if __name__ == '__main__':
  main()