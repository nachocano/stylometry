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
  parser.add_argument('-ir', '--input_raw_folder', required=True) # already in folds
  parser.add_argument('-ip', '--input_parsed_folder', required=True) # not in folds
  parser.add_argument('-op', '--output_parsed_folder', required=True)

  args = parser.parse_args()

  if not os.path.exists(args.output_parsed_folder):
    os.mkdir(args.output_parsed_folder)

  for fold in os.listdir(args.input_raw_folder):
    fold_folder = os.path.join(args.input_raw_folder, fold)
    if not os.path.isdir(fold_folder):
      continue
    output_fold_folder = os.path.join(args.output_parsed_folder, fold)
    if not os.path.exists(output_fold_folder):
      os.mkdir(output_fold_folder)
    for label in os.listdir(fold_folder):
      label_folder = os.path.join(fold_folder, label)
      if not os.path.isdir(label_folder):
        continue
      output_label_folder = os.path.join(output_fold_folder, label)
      if not os.path.exists(output_label_folder):
        os.mkdir(output_label_folder)
      for document in os.listdir(label_folder):
        parsed_in_folder = os.path.join(args.input_parsed_folder, label)
        in_parsed_doc = os.path.join(parsed_in_folder, document + '.pcfg')
        shutil.copy2(in_parsed_doc, output_label_folder)

if __name__ == '__main__':
  main()

