#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from gensim.models import word2vec
from gensim import matutils
from operator import itemgetter
import re


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int, default=100)
  parser.add_argument('-i', '--input_file', required=True)
  parser.add_argument('-o', '--output_file', required=True)
  args = parser.parse_args()

  books = defaultdict(list)
  p = re.compile(ur'^SENT_(\d+)_(\d)_(\d)_(\d)_(\d+)$')
  for line in open(args.input_file).read().splitlines():
    sentence = line.split()[0]
    search_obj = re.search(p, sentence)
    if search_obj:
      did = search_obj.group(1)
      gid = search_obj.group(2)
      fid = search_obj.group(3)
      label = search_obj.group(4)
      sentence_nr = search_obj.group(5)
      books[(did, gid, fid, label)].append(sentence_nr)

  print 'book lenght: %s' % len(books)

  i = 0
  new_books = {}
  new_books_next_idx = {}
  for line in open(args.embeddings_file).read().splitlines():
    if i == 0:
      i = 1
      continue
    sentence = line.split()
    search_obj = re.search(p, sentence[0])
    if search_obj:
      did = search_obj.group(1)
      gid = search_obj.group(2)
      fid = search_obj.group(3)
      label = search_obj.group(4)
      size = len(books[(did, gid, fid, label)])
      if (did, gid, fid, label) not in  new_books:
        new_books[(did, gid, fid, label)] = np.zeros([size,args.embeddings_dimension])
        new_books_next_idx[(did, gid, fid, label)] = 0
      new_books[(did, gid, fid, label)][new_books_next_idx[(did, gid, fid, label)]] = np.array(sentence[1:]).astype(np.float32)
      new_books_next_idx[(did, gid, fid, label)] += 1

  print 'new books length %d' % len(new_books)
  of = open(args.output_file, 'w')
  for elem in new_books:
    avg_embeddings = matutils.unitvec(new_books[elem].mean(axis=0)).astype(np.float32)
    embeddings_as_str = ' '.join(str(e) for e in avg_embeddings)
    of.write('%s %s %s %s %s\n' % (elem[0], elem[1], elem[2], elem[3], embeddings_as_str))
  of.close()

if __name__ == '__main__':
  main()

