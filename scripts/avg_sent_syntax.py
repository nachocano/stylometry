#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from operator import itemgetter
from gensim.models import word2vec
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
  p1 = re.compile(ur'^SYN(\d+)$')
  for line in open(args.input_file).read().splitlines():
    splitted = line.split()
    if len(splitted) == 0:
      continue
    sentence = splitted[0]
    syntax = splitted[1]
    sent_search_obj = re.search(p, sentence)
    syn_search_obj = re.search(p1, syntax)
    if sent_search_obj and syn_search_obj:
      did = sent_search_obj.group(1)
      gid = sent_search_obj.group(2)
      fid = sent_search_obj.group(3)
      label = sent_search_obj.group(4)
      sentence_nr = sent_search_obj.group(5)
      syn = syn_search_obj.group(1)
      books[(did, gid, fid, label)].append((sentence_nr, syn))

  print 'book length: %s' % len(books)

  emb = {}
  tick = time.time()
  print 'loading word2vec'

  def read_lines(f):
    for ii,line in enumerate(f):
      yield line

  for line in read_lines(open(args.embeddings_file, 'r')):
    if line.startswith('SENT') or line.startswith('SYN'):
      l = line.split()
      emb[l[0]] = np.array(l[1:]).astype(np.float32)
  elapsed = time.time() - tick
  print 'loaded word2vec in %s' % elapsed

  of = open(args.output_file, 'w')
  for (did, gid, fid, label) in books:
    book_embedding = []
    for sentence_nr, syn in books[(did, gid, fid, label)]:
      sentence = "SENT_%s_%s_%s_%s_%s" % (did, gid, fid, label, sentence_nr)
      syntax = "SYN%s" % syn
      sent_v = None
      syn_v = None
      if sentence in emb:
        sent_v = matutils.unitvec(emb[sentence])
      else:
        sent_v = np.zeros(args.embeddings_dimension)
      if syntax in emb:
        syn_v = matutils.unitvec(emb[syntax])
      else:
        syn_v = np.zeros(args.embeddings_dimension)        
      b = np.hstack((sent_v, syn_v))
      book_embedding.append(b)
    avg_book_embedding = matutils.unitvec(np.array(book_embedding).mean(axis=0)).astype(np.float32)
    embeddings_as_str = ' '.join(str(e) for e in avg_book_embedding)
    of.write('%s %s %s %s %s\n' % (did, gid, fid, label, embeddings_as_str))
  of.close()


if __name__ == '__main__':
  main()

