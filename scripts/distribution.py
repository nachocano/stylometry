from __future__ import division
import argparse
import numpy as np
import os
from collections import Counter

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_folder', required=True)
  parser.add_argument('-of', '--output', required=True)
  args = parser.parse_args()

  genres = {'Adventure_Stories' : 1, 'Fiction' : 2, 'Historical_Fiction': 3, 'Love_Stories': 4, 'Mystery' : 5, 'Poetry' : 6, 'Science_Fiction' : 7, 'Short_Stories' : 8}
  labels = {'failure' : 0, 'success' : 1}

  fails = Counter()
  successes = Counter()
  sucess_counts = 0
  fails_counts = 0
  for genre in os.listdir(args.input_folder):
    genre_folder = os.path.join(args.input_folder, genre)
    if not os.path.isdir(genre_folder):
      continue
    gid = genres[genre]
    for fold in os.listdir(genre_folder):
      fold_folder = os.path.join(genre_folder, fold)
      if not os.path.isdir(fold_folder):
        continue
      fid = fold[-1]
      for fail_success in os.listdir(fold_folder):
        fail_success_folder = os.path.join(fold_folder, fail_success)
        if not os.path.isdir(fail_success_folder):
          continue
        label = labels[fail_success[:-1]]
        for document in os.listdir(fail_success_folder):
          d = os.path.join(fail_success_folder, document)
          if os.path.isfile(d) and not d.startswith('.'):
            did = document[:document.find('.')] # removing extension
            for line in open(d).read().splitlines():
              line = line.strip()
              if label == labels['failure']:
                fails[line] += 1
                fails_counts += 1
              else:
                successes[line] += 1
                sucess_counts += 1

    smc = fails.most_common(20)
    out = open(args.output, 'w')

    for k,v in smc:
      if k not in successes:
        successes[k] = 0
      out.write('%s\t%s\t%s\n' % (k,v/fails_counts, successes[k]/sucess_counts))
    out.close()


if __name__ == '__main__':
  main()

