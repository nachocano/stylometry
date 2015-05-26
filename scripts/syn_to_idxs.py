import argparse
from collections import defaultdict


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--syntax_input_file', required=True) # syntax input file
  parser.add_argument('-o', '--idx_output_file', required=True) # idx output file
  args = parser.parse_args()

  idxs_dict = defaultdict(int)
  of = open(args.idx_output_file, 'w')
  for line in open(args.syntax_input_file).read().splitlines():
    doc = line.split()
    did, gid, fid, label = doc[0].split("_")
    rest = doc[1:]
    idxs = []
    for s in rest:
      idx = s.replace("SYN", "")
      idxs.append(idx)
      idxs_dict[idx] += 1
    idxs_as_str = ' '.join([str(i) for i in idxs])
    of.write('%s %s %s %s %s\n' % (did, gid, fid, label, idxs_as_str))
  print len(idxs_dict)

if __name__ == '__main__':
  main()  