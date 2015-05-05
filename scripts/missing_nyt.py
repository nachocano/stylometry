from __future__ import division
import argparse
import numpy as np
import os
from collections import Counter

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_folder', required=True)
  parser.add_argument('-g', '--great_file', required=True)
  parser.add_argument('-t', '--typical_file', required=True)
  parser.add_argument('-v', '--very_good_file', required=True)
  args = parser.parse_args()

  labels = {'great' : 0, 'verygood' : 1, 'typical' : 2}

  dictionary = {}
  populate_dict(dictionary, args.great_file)
  populate_dict(dictionary, args.typical_file)
  populate_dict(dictionary, args.very_good_file)

  print 'total files %d' % len(dictionary)

  total_docs = 0
  for label in os.listdir(args.input_folder):
    label_folder = os.path.join(args.input_folder, label)
    if not os.path.isdir(label_folder):
      continue
    lid = labels[label]
    for document in os.listdir(label_folder):
      assert document in dictionary
      dictionary[document] = True
      total_docs += 1

  missing = 0
  for k in dictionary:
    if dictionary[k] == False:
      print k
      missing +=1
  
  print 'nenkova total %s' % len(dictionary)
  print 'total downloaded %s' % total_docs
  print 'missing files %s' % missing

def populate_dict(dictionary, filename):
  for line in open(filename).read().splitlines():
    dictionary[line] = False
            
if __name__ == '__main__':
  main()

