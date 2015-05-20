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
  parser.add_argument('-i', '--input_file', required=True)
  parser.add_argument('-o', '--output_file', required=True)
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

  articles = {}
  counts = defaultdict(int)
  for line in open(args.input_file).read().splitlines():
    line_splitted = line.split()
    if is_validation:
      _, did, label = line_splitted[0].split("-")
      key = (did, label)
    else:
      _, did, fold, label = line_splitted[0].split("-")
      key = (did, fold, label)
    
    assert key not in articles
    words = line_splitted[1:]
    articles[key] = np.zeros(args.embeddings_dimension)
    for word in words:
      word = word.strip()
      assert model.__contains__(word)
      articles[key] += model.syn0[model.vocab[word].index]
      counts[key] += 1

  print 'articles length: %s' % len(articles)

  of = open(args.output_file, 'w')
  for key in articles:
    embedding = matutils.unitvec(articles[key] / articles[key]).astype(np.float32)
    embedding_as_str = ' '.join(str(e) for e in embedding)
    year, month, day, identifier = key[0].split("_")
    if is_validation:
      of.write('%s %d %d %s %s %s\n' % (year, int(month), int(day), identifier, key[1], embedding_as_str))
    else:  
      of.write('%s %d %d %s %s %s %s\n' % (year, int(month), int(day), identifier, key[1], key[2], embedding_as_str))
  
  of.close()

if __name__ == '__main__':
  main()