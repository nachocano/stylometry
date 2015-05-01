from __future__ import division
import argparse
import numpy as np
import os
from collections import Counter

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_folder', required=True)
  args = parser.parse_args()

  labels = {'great' : 0, 'verygood' : 1, 'typical' : 2}

  for label in os.listdir(args.input_folder):
    label_folder = os.path.join(args.input_folder, label)
    if not os.path.isdir(label_folder):
      continue
    lid = labels[label]
    for document in os.listdir(label_folder):
      d = os.path.join(label_folder, document)
      if os.path.isfile(d) and not d.startswith('.'):
        did = document[:document.find('.')] # removing extension
        i = 0
        for line in open(d).read().splitlines():
          print 'SENT-%s-%s-%d %s' % (did, lid, i, line) # check for -, not underscore
          i += 1
            
if __name__ == '__main__':
  main()

