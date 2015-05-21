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
  args = parser.parse_args()

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
    did, gid, fid, label = line_splitted[0].split("_")
    key = '%s_%s_%s_%s' % (did, gid, fid, label)
    embedding = matutils.unitvec(model.syn0[model.vocab[key].index]).astype(np.float32)
    embedding_as_str = ' '.join(str(e) for e in embedding)    
    of.write('%s %s %s %s %s\n' % (did, gid, fid, label, embedding_as_str))
  of.close()

if __name__ == '__main__':
  main()