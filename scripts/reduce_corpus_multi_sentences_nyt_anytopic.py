from __future__ import division
import argparse
import numpy as np
import os
import re

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_folder', required=True)
  parser.add_argument('-i', '--input_file_all', required=True)
  args = parser.parse_args()

  labels = {'verygood' : 1, 'typical' : 2}

  documents = {}
  for fold in os.listdir(args.input_folder):
    fold_folder = os.path.join(args.input_folder, fold)
    if not os.path.isdir(fold_folder):
      continue
    for label in os.listdir(fold_folder):
      label_folder = os.path.join(fold_folder, label)
      if not os.path.isdir(label_folder):
        continue
      for document in os.listdir(label_folder):
        did = document[:document.find('.')] # removing extension
        assert did not in documents
        documents[did] = (labels[label], int(fold.replace('fold','')))

  p = re.compile(ur'^SENT-(\d{4}_\d{2}_\d{2}_\d+)-(\d)-(\d+)$')
  for line in open(args.input_file_all).read().splitlines():
    splitted = line.split()
    sentence = splitted[0]
    search_obj = re.search(p, sentence)
    if search_obj:
      did = search_obj.group(1)
      label = search_obj.group(2)
      sentence_nr = search_obj.group(3)
      if did in documents:
        that_label, fold = documents[did]
        assert int(label) == int(that_label)
        line_as_str = ' '.join(str(e) for e in splitted[1:])
        print 'SENT-%s-%d-%d-%d %s' % (did, fold, int(label), int(sentence_nr), line_as_str)

if __name__ == '__main__':
  main()

