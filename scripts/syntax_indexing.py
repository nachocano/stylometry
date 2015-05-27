from __future__ import division
import argparse
import numpy as np
import os
from collections import Counter, defaultdict

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-rif', '--raw_input_folder', required=True)
  parser.add_argument('-pif', '--parsed_input_folder', required=True)
  parser.add_argument('-of', '--output_file', required=True)
  parser.add_argument('-ov', '--output_vocab', required=True)
  parser.add_argument('-or', '--output_raw', required=True)
  parser.add_argument('-e', '--embedding_file', required=True)
  args = parser.parse_args()

  genres = {'Adventure_Stories' : 1, 'Fiction' : 2, 'Historical_Fiction': 3, 'Love_Stories': 4, 'Mystery' : 5, 'Poetry' : 6, 'Science_Fiction' : 7, 'Short_Stories' : 8}
  labels = {'failure' : 0, 'success' : 1}

  of = open(args.output_file, 'w')
  ov = open(args.output_vocab, 'w')
  oraw = open(args.output_raw, 'w')
  index = 0
  dictionary = Counter()
  mapping = {}
  mapping_raw = defaultdict(list)
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
            new_words = []
            i = 0
            with open(d_raw) as f1, open(d_parsed) as f2:
              j = 0
              for l_raw, l_parsed in zip(f1, f2):
                # just use the 100 first sentences
                if j == 100:
                  break
                parsed = l_parsed.strip()
                if parsed not in mapping:
                  #mapping[parsed] = 'SYN%d' % index
                  mapping[parsed] = index
                  ov.write('%s\t%s\n' % (mapping[parsed], parsed))
                  index +=1
                dictionary[mapping[parsed]] += 1
                mapping_raw[mapping[parsed]].append(l_raw.rstrip())
                new_words.append(mapping[parsed])
                j += 1
            new_words_as_str = ' '.join(str(e) for e in new_words)
            of.write('%s %s %s %s %s\n' % (did, gid, fid, label, new_words_as_str))
            #of.write('%s\n' % (new_words_as_str))
  
  for key in mapping_raw:
    sentences = mapping_raw[key]
    sentences_as_str = '|^^|'.join(str(e) for e in sentences)
    oraw.write('%s\t%s\n' % (key, sentences_as_str))
  oraw.close()
  of.close()
  ov.close()

  print dictionary.most_common(50)

if __name__ == '__main__':
  main()
