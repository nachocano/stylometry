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


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int)
  parser.add_argument('-i', '--input_file', required=True) # the reduced file or the validation file
  parser.add_argument('-o', '--output_file', required=True) # features
  parser.add_argument('-m', '--mode', required=True, default='n')
  args = parser.parse_args()

  assert args.mode == 'v' or args.mode == 'n'
  is_validation = args.mode == 'v'

  if not args.embeddings_dimension:
    args.embeddings_dimension = 100

  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=False)
  model.init_sims()
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed

  of = open(args.output_file, 'w')
  for line in open(args.input_file).read().splitlines():
    line_splitted = line.split()
    if is_validation:
      _, did, label = line_splitted[0].split("-")
    else:
      _, did, fold, label = line_splitted[0].split("-")
    
    key = 'DOC_%s_%s' % (did, label)
    embedding = model.syn0[model.vocab[key].index]
    embedding_as_str = ' '.join(str(e) for e in embedding)
    year, month, day, identifier = did.split("_")
    if is_validation:
      of.write('%s %d %d %s %s %s\n' % (year, int(month), int(day), identifier, label, embedding_as_str))
    else:
      of.write('%s %d %d %s %s %s %s\n' % (year, int(month), int(day), identifier, fold, label, embedding_as_str))
  of.close()

if __name__ == '__main__':
  main()