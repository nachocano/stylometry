from __future__ import division
import argparse
import numpy as np
import utils

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-rif', '--raw_folder', required=True)
  parser.add_argument('-pif', '--parsed_folder', required=True)
  parser.add_argument('-v', '--verbose', required=False, type=int, default=1)
  parser.add_argument('-d', '--embedding_dimension', required=False, type=int, default=100)
  parser.add_argument('-ne', '--epochs', required=False, type=int, default=10)
  parser.add_argument('-c', '--corpus', required=False, default='novels')

  args = parser.parse_args()

  # valid corpus so far
  assert args.corpus == 'novels' or args.corpus == 'nyt'

  data, syn_data = utils.read_data(args.raw_folder, args.parsed_folder, args.corpus)
  words2idx = data[1]
  orig_size = len(words2idx)
  words2idx_syn = syn_data[1]
  idx2word  = dict((k,v) for v,k in words2idx.iteritems())
  idx2word_syn  = dict((k,v) for v,k in words2idx_syn.iteritems())

  for key in idx2word_syn:
    idx2word[key + orig_size] = idx2word_syn[key]
  words2idx  = dict((k,v) for v,k in idx2word.iteritems())

  new_syn_data = []
  for ids, novel in syn_data[0]:
    new_novel = []
    for sentence in novel:
      new_novel.append(sentence + orig_size)
    new_syn_data.append((ids, new_novel))

  # assert
  for d, s in zip(data[0], new_syn_data[0]):
      assert d[0] == s[0]

if __name__ == '__main__':
  main()

