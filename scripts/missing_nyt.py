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
  parser.add_argument('-go', '--great_file_out', required=True)
  parser.add_argument('-to', '--typical_file_out', required=True)
  parser.add_argument('-vo', '--very_good_file_out', required=True)
  args = parser.parse_args()

  labels = {'great' : 0, 'verygood' : 1, 'typical' : 2}

  great_dict = populate_dict(args.great_file)
  typical_dict = populate_dict(args.typical_file)
  very_good_dict = populate_dict(args.very_good_file)

  print 'total files %d' % (len(great_dict) + len(typical_dict) + len(very_good_dict))

  total_docs = 0
  for label in os.listdir(args.input_folder):
    label_folder = os.path.join(args.input_folder, label)
    if not os.path.isdir(label_folder):
      continue
    lid = labels[label]
    for document in os.listdir(label_folder):
      if lid == 0:
        assert document in great_dict
        great_dict[document] = True
      elif lid == 1:
        assert document in very_good_dict
        very_good_dict[document] = True
      elif lid == 2:
        assert document in typical_dict
        typical_dict[document] = True
      else: 
        raise Exception
      total_docs += 1

  missing = 0
  go = open(args.great_file_out, 'w')
  to = open(args.typical_file_out, 'w')
  vo = open(args.very_good_file_out, 'w')
  for k in great_dict:
    if great_dict[k] == False:
      go.write('%s\n' % k)
      missing +=1
  for k in typical_dict:
    if typical_dict[k] == False:
      to.write('%s\n' % k)
      missing +=1
  for k in very_good_dict:
    if very_good_dict[k] == False:
      vo.write('%s\n' % k)
      missing +=1
  
  print 'nenkova total %s' % (len(great_dict) + len(typical_dict) + len(very_good_dict))
  print 'total downloaded %s' % total_docs
  print 'missing files %s' % missing

def populate_dict(filename):
  dictionary = {}
  for line in open(filename).read().splitlines():
    dictionary[line] = False
  return dictionary
            
if __name__ == '__main__':
  main()

