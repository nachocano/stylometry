from __future__ import division
import argparse
import numpy as np
import os
from collections import defaultdict

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_folder', required=True) # nyttext
  parser.add_argument('-i', '--input_file', required=True) # validation any topic
  args = parser.parse_args()

  labels = {'verygood' : 1, 'typical' : 2}

  dictionary = defaultdict(list)
  for line in open(args.input_file).read().splitlines():
    vg, typical = line.split()
    dictionary[labels['verygood']].append(vg)
    dictionary[labels['typical']].append(typical)

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
        i = 0
        for line in open(d).read().splitlines():
          print 'SENT-%s-%s-%d %s' % (did, lid, i, line) # check for -, not underscore
          i += 1
            
if __name__ == '__main__':
  main()

