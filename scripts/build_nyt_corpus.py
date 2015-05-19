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
from collections import defaultdict

def read_pairs(filename):
  pairs = []
  pairs_as_dict = {}
  for line in open(filename).read().splitlines():
    line = line.split('\t')
    vg = line[0]
    typicals = line[2:]
    typs = [t.split(':')[0] for t in typicals]
    pairs.append((vg, typs))
    pairs_as_dict[vg] = typs
  return pairs, pairs_as_dict


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-p', '--pairs_file', required=True)
  parser.add_argument('-if', '--input_folder', required=True)
  parser.add_argument('-ofs', '--output_folder_same', required=True)
  parser.add_argument('-ofa', '--output_folder_any', required=True)
  parser.add_argument('-vf', '--validation_folder', required=True)
  args = parser.parse_args()

  labels = {'verygood' : 1, 'typical' : 2}

  pairs, pairs_as_dict = read_pairs(args.pairs_file)

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

  random.seed(37)

  # create validation set
  missing = 100
  validation_same_topic = []
  unique_vgs = {}
  unique_typs = {}
  while missing != 0:
    rnds = random.sample(xrange(len(pairs)), 100)
    for idx in rnds:
      assert len(pairs[idx][1]) == 10
      vg, typs = pairs[idx]
      if vg in all_documents['verygood'] and vg not in unique_vgs:
        count = 0
        candidates = []
        for typ in typs:
          if typ in all_documents['typical'] and typ not in unique_typs:
            count += 1
            candidates.append(typ)
        if count == 10:
          validation_same_topic.append((vg, candidates))
          unique_vgs[vg] = True
          for c in candidates:
            unique_typs[c] = True
          missing -= 1
          #print 'added vg, missing %d' % missing
          if missing == 0:
            break

  # VALIDATION SET

  validation_any_topic = []
  for v in validation_same_topic:
    idx = random.sample(xrange(10), 1)
    validation_any_topic.append((v[0], v[1][idx[0]]))

  vat_file = os.path.join(args.validation_folder, 'valid_any_topic.txt')
  vat = open(vat_file, 'w')
  for v in validation_any_topic:
    vat.write('%s %s\n' % (v[0], v[1]))
  vat.close()

  vst_file = os.path.join(args.validation_folder, 'valid_same_topic.txt')
  vst = open(vst_file, 'w')
  for v in validation_same_topic:
    as_str = ' '.join(str(s) for s in v[1])
    vst.write('%s %s\n' % (v[0], as_str))
  vat.close()


  #################### SAME TOPIC dataset  ################################

  new_unique_vgs = {}
  new_unique_typs = {}
  files , missing = 3430, 3430
  same_topic = []
  vgs = random.sample(list(set(all_documents['verygood']) - set(unique_vgs.keys())), files)
  for vg in vgs:
    assert len(pairs_as_dict[vg]) == 10
    typs = pairs_as_dict[vg]
    for typ in typs:
      assert typ in all_documents['typical']
    same_topic.append((vg, typs))

  # saving the different chunks
  folds = 10  
  chunks = int(math.ceil(files/folds))
  indexes = range(files)
  splitted = [indexes[i:i+chunks] for i in range(0,len(indexes),chunks)]
  for i in xrange(folds):
    print 'saving fold %d' % i
    fid = os.path.join(args.output_folder_same, '%d.txt' % (i+1))
    out = open(fid, 'w')
    for idx in splitted[i]:
      v1, v2 = same_topic[idx]
      assert len(v2) == 10
      new_as_str = ' '.join(str(v) for v in v2)
      out.write('%s %s\n' % (v1, new_as_str))
    out.close()


  ########## ANY TOPIC dataset #####################
  #files = 3430
  #folds = 10
  #very_good_articles = random.sample(list(set(all_documents['verygood']) - set(unique_vgs.keys())), files)
  very_good_articles = [a[0] for a in same_topic]
  typical_articles = random.sample(list(set(all_documents['typical']) - set(unique_typs.keys())), files)

  # works in place and returns None
  random.shuffle(very_good_articles)
  random.shuffle(typical_articles)

  subsampled = {'verygood' : very_good_articles, 'typical' : typical_articles}

  # making folds folders
  if not os.path.exists(args.output_folder_any):
    os.mkdir(args.output_folder_any)
  for i in xrange(folds):
    fold_directory = os.path.join(args.output_folder_any, 'fold%d' % (i+1))
    if not os.path.exists(fold_directory):
      os.mkdir(fold_directory)

  # saving the different chunks
  chunks = int(math.ceil(files/folds))
  indexes = range(files)
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
        output_directory = os.path.join(args.output_folder_any, 'fold%s' % (i+1))
        out_dir = os.path.join(output_directory, label)
        if not os.path.exists(out_dir):
          os.mkdir(out_dir)
        shutil.copy2(in_file, out_dir)
        
if __name__ == '__main__':
  main()

