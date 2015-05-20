from __future__ import division
import argparse
import numpy as np
import os
from collections import defaultdict
import re

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_folder', required=True) # nyttext
  parser.add_argument('-i', '--input_file', required=True) # validation any topic
  parser.add_argument('-a', '--input_file_all', required=True) # all syntax file (not the reduced one)
  args = parser.parse_args()

  labels = {'verygood' : 1, 'typical' : 2}

  dictionary = defaultdict(list)
  for line in open(args.input_file).read().splitlines():
    vg, typical = line.split()
    dictionary[labels['verygood']].append(vg)
    dictionary[labels['typical']].append(typical)

  articles = []
  for label in os.listdir(args.input_folder):
    if label not in labels.keys():
      continue
    label_folder = os.path.join(args.input_folder, label)
    if not os.path.isdir(label_folder):
      continue
    lid = labels[label]
    for document in os.listdir(label_folder):
      if document not in dictionary[lid]:
        continue
      d = os.path.join(label_folder, document)
      if os.path.isfile(d) and not d.startswith('.'):
        did = document[:document.find('.')] # removing extension
        articles.append((did, lid))

  p = re.compile(ur'^DOC_(\d{4}_\d{2}_\d{2}_\d+)_(\d)$')
  for line in open(args.input_file_all).read().splitlines():
    splitted = line.split()
    sentence = splitted[0]
    search_obj = re.search(p, sentence)
    if search_obj:
      did = search_obj.group(1)
      label = int(search_obj.group(2))
      if (did, label) in articles:
        line_as_str = ' '.join(str(e) for e in splitted[1:])
        print 'DOC-%s-%d %s' % (did, label, line_as_str)

if __name__ == '__main__':
  main()

