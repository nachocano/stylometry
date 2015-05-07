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
  word2idx = {}
  idx2word = {}
  pcfg2syn = {}
  syn2idx = {}
  idx2syn = {}
  word_index = 0
  syn_index = 0
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
            sentences = []
            with open(d_raw) as f1, open(d_parsed) as f2:
              for l_raw, l_parsed in zip(f1, f2):
                parsed = l_parsed.strip()
                # first syns
                if parsed not in pcfg2syn:
                  pcfg2syn[parsed] = 'SYN%d' % syn_index
                  syn2idx[pcfg2syn[parsed]] = syn_index
                  idx2syn[syn_index] = pcfg2syn[parsed]
                  syn_index += 1
                  om.write('%s\t%s\n' % (pcfg2syn[parsed], parsed))
                syn_counts[pcfg2syn[parsed]] += 1
                syns.append(syn2idx[pcfg2syn[parsed]])

                # then words
                l_raw = l_raw.lower()
                ws = l_raw.rstrip().split()
                sentences.append((pcfg2syn[parsed], ws))
                
                '''
                sentence = []
                ws = l_raw.rstrip().split()
                for w in ws:
                  w = w.lower()
                  word_counts[w] += 1
                  if w not in word2idx:
                    word2idx[w] = word_index
                    idx2word[word_index] = w
                    word_index += 1
                  sentence.append(word2idx[w])
                sentences.append(sentence)
                '''
            
            # first syns
            syns_arrays = utils.contextwin(syns, args.context_window)
            for array in syns_arrays:
              mid = int(len(array)/2)
              w = idx2syn[array[mid]]
              for left in array[:mid]:
                if left == -1:
                  continue
                of.write('%s %s\n' % (w, idx2syn[left]))
                cxt_counts[idx2syn[left]] += 1
              for right in array[mid+1:]:
                if right == -1:
                  continue
                of.write('%s %s\n' % (w, idx2syn[right]))
                cxt_counts[idx2syn[right]] += 1

            # then sentences, words are only contexts of SYN
            # maybe should do some downsampling here, based on word frequencies or something
            # for later
            for s, sent in sentences:
              for w in sent:
                of.write('%s %s\n' % (s, w))
                cxt_counts[w] += 1
            
            '''
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
            '''

  of.close()  
  om.close()
  # save vocabulary counts (word count)
  ov = open(args.output_vocabulary, 'w')
  # save word counts (just syns are words)
  for syn in syn_counts:
    ov.write('%s %d\n' % (syn, syn_counts[syn]))
  ov.close()  
  # save contexts counts
  oc = open(args.output_contexts, 'w')
  for cxt in cxt_counts:
    oc.write('%s %d\n' % (cxt, cxt_counts[cxt]))
  oc.close()




if __name__ == '__main__':
  main()
