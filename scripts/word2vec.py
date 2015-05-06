from __future__ import division
import argparse
import numpy as np
import utils

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-rif', '--raw_folder', required=True)
  parser.add_argument('-pif', '--parsed_folder', required=True)
  parser.add_argument('-v', '--verbose', required=False, type=int, default=1)
  parser.add_argument('-d', '--embedding_dimension', required=False, type=int, default=100)
  parser.add_argument('-ne', '--epochs', required=False, type=int, default=10)
  parser.add_argument('-c', '--corpus', required=False, default='novels')

  args = parser.parse_args()

  # valid corpus so far
  assert args.corpus == 'novels' or args.corpus == 'nyt'

  data, syn_data = utils.read_data(args.raw_folder, args.parsed_folder, args.corpus)


if __name__ == '__main__':
  main()

