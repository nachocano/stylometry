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
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int, default=100)
  parser.add_argument('-i', '--input_file', required=True) # validation file
  parser.add_argument('-o', '--output_file', required=True)
  args = parser.parse_args()

  labels = {'verygood' : 1, 'typical' : 2}  

  nyt = defaultdict(list)
  p = re.compile(ur'^SENT-(\d{4}_\d{2}_\d{2}_\d+)-(\d)-(\d+)$')
  # did, label, sentence_nr
  for line in open(args.input_file).read().splitlines():
    splitted = line.split()
    sentence = splitted[0]
    search_obj = re.search(p, sentence)
    if search_obj:
      did = search_obj.group(1)
      label = int(search_obj.group(2))
      sentence_nr = int(search_obj.group(3))
      nyt[(did, label)].append(sentence_nr)

  print 'nyt length: %s' % len(nyt)

  p1 = re.compile(ur'^SENT-(\d{4}_\d{2}_\d{2}_\d+)-(\d)-(\d+)$')
  i = 0
  new_nyt = {}
  new_nyt_next_idx = {}
  for line in open(args.embeddings_file).read().splitlines():
    if i == 0:
      i = 1
      continue
    sentence = line.split()
    search_obj = re.search(p1, sentence[0])
    if search_obj:
      did = search_obj.group(1)
      label = int(search_obj.group(2))
      sentence_nr = int(search_obj.group(3))
      size = len(nyt[(did, label)])
      if (did, label) not in  new_nyt and len(nyt[(did, label)]) > 0:
        new_nyt[(did, label)] = np.zeros([size,args.embeddings_dimension])
        new_nyt_next_idx[(did, label)] = 0
      if (did, label) in  new_nyt:
        new_nyt[(did, label)][new_nyt_next_idx[(did, label)]] = np.array(sentence[1:]).astype(np.float32)
        new_nyt_next_idx[(did, label)] += 1

  print 'new nyt length %d' % len(new_nyt)
  of = open(args.output_file, 'w')
  for elem in new_nyt:
    avg_embeddings = matutils.unitvec(new_nyt[elem].mean(axis=0)).astype(np.float32)
    embeddings_as_str = ' '.join(str(e) for e in avg_embeddings)
    did = elem[0]
    year, month, day, identifier = did.split("_")
    label = elem[1]
    of.write('%s %d %d %s %s %s %s\n' % (year, int(month), int(day), identifier, label, embeddings_as_str))
  of.close()

if __name__ == '__main__':
  main()

