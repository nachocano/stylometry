from __future__ import division
import argparse
import numpy as np
import os
import pdb
from collections import Counter, defaultdict
import utils
from copy import deepcopy
from gensim import matutils

def entries(filename):
  def read_lines(f):
    for ii,line in enumerate(f):
      yield line

  dictionary = {}
  for line in read_lines(open(filename, 'r')):
    if line.startswith('SYN')
      splitted = line.split()
      key = splitted[0]
      dictionary[key] = splitted[1:]
  return dictionary

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-rif', '--raw_input_folder', required=True)
  parser.add_argument('-pif', '--parsed_input_folder', required=True)
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-c', '--contexts_file', required=False)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int, default=100)

  args = parser.parse_args()

  genres = {'Adventure_Stories' : 1, 'Fiction' : 2, 'Historical_Fiction': 3, 'Love_Stories': 4, 'Mystery' : 5, 'Poetry' : 6, 'Science_Fiction' : 7, 'Short_Stories' : 8}
  labels = {'failure' : 0, 'success' : 1}

  use_context = True if args.contexts_file else False

  embs = entries(args.embeddings_file)
  if use_context:
    cxts = entries(args.contexts_file)

  pcfg2idx = {}
  pcfg_index = 0
  for genre in os.listdir(args.raw_input_folder):
    genre_folder_raw = os.path.join(args.raw_input_folder, genre)
    genre_folder_parsed = os.path.join(args.parsed_input_folder, genre)
    if not os.path.isdir(genre_folder_raw):
      continue
    gid = genres[genre]
    for fold in os.listdir(genre_folder_raw):
      fold_folder_raw = os.path.join(genre_folder_raw, fold)
      fold_folder_parsed = os.path.join(genre_folder_parsed, fold)
      if not os.path.isdir(fold_folder_raw):
        continue
      fid = fold[-1]
      for fail_success in os.listdir(fold_folder_raw):
        fail_success_folder_raw = os.path.join(fold_folder_raw, fail_success)
        fail_success_folder_parsed = os.path.join(fold_folder_parsed, fail_success)
        if not os.path.isdir(fail_success_folder_raw):
          continue
        label = labels[fail_success[:-1]]
        for document in os.listdir(fail_success_folder_raw):
          d_raw = os.path.join(fail_success_folder_raw, document)
          d_parsed = os.path.join(fail_success_folder_parsed, document + ".lpcfg")
          if os.path.isfile(d_raw) and not d_raw.startswith('.') and os.path.isfile(d_parsed) and not d_parsed.startswith('.'):
            did = document[:document.find('.')] # removing extension
            syns = []
            words = []
            with open(d_raw) as f1, open(d_parsed) as f2:
              for l_raw, l_parsed in zip(f1, f2):
                parsed = l_parsed.strip()
                # first syns
                if parsed not in pcfg2idx:
                  pcfg2idx[parsed] = 'SYN%d' % pcfg_index
                  pcfg_index +=1
                syns.append(pcfg2idx[parsed])

                # then words
                #ws = l_raw.rstrip().split()
                #for w in ws:
                #  words.append(w.lower())
            
            p = 2 if use_context else 1
            result = np.zeros([len(syns), args.embeddings_dimension * p])
            for i, syn in enumerate(syns):
              if str(syn) not in embs:
                print 'key %s not found' % syn
                continue
              #e = deepcopy(embs[str(syn)])
              #if use_context:
              #  e.extend(cxts['SYN%d' % syn])
              result[i] = np.array(embs[str(syn)])
            avg_embeddings = matutils.unitvec(result.mean(axis=0)).astype(np.float32)
            embeddings_as_str = ' '.join(str(e) for e in avg_embeddings)
            print '%s %s %s %s %s' % (did, gid, fid, label, embeddings_as_str)

if __name__ == '__main__':
  main()
