#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
import os
import random
import math
import shutil


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_folder', required=True)
  parser.add_argument('-of', '--output_folder', required=True)
  args = parser.parse_args()

  labels = {'verygood' : 1, 'typical' : 2}

  all_documents = defaultdict(list)
  for label in os.listdir(args.input_folder):
    label_folder = os.path.join(args.input_folder, label)
    if not os.path.isdir(label_folder) or label not in labels:
      continue
    for document in os.listdir(label_folder):
      d = os.path.join(label_folder, document)
      if os.path.isfile(d) and not d.startswith('.'):
        #did = document[:document.find('.')] # removing extension
        all_documents[label].append(document)

  size = len(all_documents['verygood'])
  # getting same amount of typical docs
  typical_docs_any_topics = random.sample(all_documents['typical'], size)

  # works in place and returns None
  random.shuffle(all_documents['verygood'])
  random.shuffle(typical_docs_any_topics)

  subsampled = {'verygood' : all_documents['verygood'], 'typical' : typical_docs_any_topics}

  # making folds folders
  if not os.path.exists(args.output_folder):
    os.mkdir(args.output_folder)
  folds = 10
  for i in xrange(folds):
    fold_directory = os.path.join(args.output_folder, 'fold%d' % (i+1))
    if not os.path.exists(fold_directory):
      os.mkdir(fold_directory)

  # saving the different chunks
  chunks = int(math.ceil(size/folds))
  indexes = range(size)
  splitted = [indexes[i:i+chunks] for i in range(0,len(indexes),chunks)]
  for label in labels:
    print 'label %s' % label
    for i in xrange(folds):
      print 'copying fold %d' % i
      for idx in splitted[i]:
        # file name
        name = subsampled[label][idx]
        input_directory = os.path.join(args.input_folder, label)
        in_file = os.path.join(input_directory, name)
        output_directory = os.path.join(args.output_folder, 'fold%s' % (i+1))
        out_dir = os.path.join(output_directory, label)
        if not os.path.exists(out_dir):
          os.mkdir(out_dir)
        shutil.copy2(in_file, out_dir)
        
if __name__ == '__main__':
  main()

