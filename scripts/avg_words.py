#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from operator import itemgetter


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

  books = {}
  counts = {}
  p = re.compile(ur'^_\*(\d+)_(\d)_(\d)_(\d)$')
  for line in open(args.input_file).read().splitlines():
    line_splitted = line.split()
    sentence = line_splitted[0]
    search_obj = re.search(p, sentence)
    if search_obj:
      did = search_obj.group(1)
      gid = search_obj.group(2)
      fid = search_obj.group(3)
      label = search_obj.group(4)
      key = (did, gid, fid, label)
      if not books[key]:
        books[key] = np.zeros(args.embeddings_dimension)
      for word in line_splitted[1:]:
        word = word.strip()
        if model.__contains__(word):
          books[key] += model.syn0[model.vocab[word].index]
          counts[key] += 1

  print 'book length: %s' % len(books)  
  of = open(args.output_file, 'w')
  for key in books:
    embedding = matutils.unitvec(books[key] / counts[key]).astype(np.float32)   
    embedding_as_str = ' '.join(str(e) for e in embedding)
    of.write('%s %s %s %s %s\n' % (key[0], key[1], key[2], key[3], embedding_as_str))
  of.close()

if __name__ == '__main__':
  main()

