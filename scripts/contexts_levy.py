from __future__ import division
import argparse
import numpy as np
import os
import pdb
from collections import Counter, defaultdict
import utils

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-rif', '--raw_input_folder', required=True)
  parser.add_argument('-pif', '--parsed_input_folder', required=True)
  parser.add_argument('-of', '--output_file', required=True)
  parser.add_argument('-ov', '--output_vocabulary', required=True)
  parser.add_argument('-oc', '--output_contexts', required=True)
  parser.add_argument('-om', '--output_mapping', required=True)
  parser.add_argument('-c', '--context_window', required=True, type=int, default=10)

  args = parser.parse_args()

  genres = {'Adventure_Stories' : 1, 'Fiction' : 2, 'Historical_Fiction': 3, 'Love_Stories': 4, 'Mystery' : 5, 'Poetry' : 6, 'Science_Fiction' : 7, 'Short_Stories' : 8}
  labels = {'failure' : 0, 'success' : 1}

  om = open(args.output_mapping, 'w')
  of = open(args.output_file, 'w')
  word_counts = Counter()
  syn_counts = Counter()
  cxt_counts = Counter()
  pcfg2idx = {}
  word2idx = {}
  idx2word = {}
  pcfg_index = 0
  word_index = 0
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
          print 'processing document %s' % document
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
                  pcfg2idx[parsed] = pcfg_index
                  om.write('SYN%d\t%s\n' % (pcfg2idx[parsed], parsed))
                  pcfg_index +=1
                syn_counts[pcfg2idx[parsed]] += 1
                syns.append(pcfg2idx[parsed])

                # then words
                ws = l_raw.rstrip().split()
                for w in ws:
                  w = w.lower()
                  word_counts[w] += 1
                  if w not in word2idx:
                    word2idx[w] = word_index
                    idx2word[word_index] = w
                    word_index += 1
                  words.append(word2idx[w])
            
            # first syns
            syns_arrays = utils.contextwin(syns, args.context_window)
            for array in syns_arrays:
              mid = int(len(array)/2)
              w = 'SYN%d' % array[mid]
              for left in array[:mid]:
                of.write('%s %s\n' % (w, 'SYN%d' % left))
                cxt_counts['SYN%d' % left] += 1
              for right in array[mid+1:]:
                of.write('%s %s\n' % (w, 'SYN%d' % right))
                cxt_counts['SYN%d' % right] += 1

            # then words
            idx2word[-1] = 'padding'
            word2idx['padding'] = -1
            words_arrays = utils.contextwin(words, args.context_window)
            for array in words_arrays:
              mid = int(len(array)/2)
              w = idx2word[array[mid]]
              for left in array[:mid]:
                of.write('%s %s\n' % (w, idx2word[left]))
                cxt_counts[idx2word[left]] += 1
              for right in array[mid+1:]:
                of.write('%s %s\n' % (w, idx2word[right]))
                cxt_counts[idx2word[right]] += 1

  om.close()
  # save vocabulary counts (word count)
  ov = open(args.output_vocabulary, 'w')
  for word in word_counts:
    ov.write('%s %d\n' % (word, word_counts[word]))
  for syn in syn_counts:
    ov.write('%s %d\n' % (syn, syn_counts[syn]))
  ov.close()  

  # save contexts counts
  oc = open(args.output_contexts, 'w')
  for cxt in cxt_counts:
    oc.write('%s %d\n' % (cxt, cxt_counts[cxt]))
  oc.close()
  of.close()



if __name__ == '__main__':
  main()
