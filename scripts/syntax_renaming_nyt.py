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
  args = parser.parse_args()

  labels = {'great' : 0, 'verygood' : 1, 'typical' : 2}

  of = open(args.output_file, 'w')
  index = 0
  dictionary = Counter()
  mapping = {}
  for vg_typ_great in os.listdir(args.raw_input_folder):
    vg_typ_great_folder_raw = os.path.join(args.raw_input_folder, vg_typ_great)
    vg_typ_great_folder_parsed = os.path.join(args.parsed_input_folder, vg_typ_great)
    if not os.path.isdir(vg_typ_great_folder_raw):
      continue
    label = labels[vg_typ_great]
    for document in os.listdir(vg_typ_great_folder_raw):
      print document
      d_raw = os.path.join(vg_typ_great_folder_raw, document)
      d_parsed = os.path.join(vg_typ_great_folder_parsed, document + ".lpcfg")
      if os.path.isfile(d_raw) and not d_raw.startswith('.') and os.path.isfile(d_parsed) and not d_parsed.startswith('.'):
        did = document[:document.find('.')] # removing extension
        new_words = []
        i = 0
        with open(d_raw) as f1, open(d_parsed) as f2:
          for l_raw, l_parsed in zip(f1, f2):
            parsed = l_parsed.strip()
            if parsed not in mapping:
              mapping[parsed] = 'SYN%d' % index
              index +=1
            dictionary[mapping[parsed]] += 1
            new_words.append(mapping[parsed])
        new_words_as_str = ' '.join(str(e) for e in new_words)
        of.write('DOC_%s_%s %s\n' % (did, label, new_words_as_str))
  
  of.close()

  print dictionary.most_common(50)

if __name__ == '__main__':
  main()
