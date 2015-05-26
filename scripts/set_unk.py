import argparse
from collections import defaultdict
from collections import Counter, OrderedDict


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--idx_input_file', required=True) # ixs input file
  parser.add_argument('-o', '--idx_output_file', required=True) # idx output file
  parser.add_argument('-t', '--threshold', required=True, type=int)
  args = parser.parse_args()

  idxs_counter = Counter()
  of = open(args.idx_output_file, 'w')
  docs = OrderedDict()
  for line in open(args.idx_input_file).read().splitlines():
    doc = line.split()
    did, gid, fid, label = doc[0], doc[1], doc[2], doc[3]
    rest = doc[4:]
    for s in rest:
      idxs_counter[s] += 1
    docs[(did, gid, fid, label)] = rest

  unk = 0
  replaced = Counter()
  new_vocab = set()
  new_idx = 1
  new_idxs_map = {}
  for key in docs:
    did, gid, fid, label = key[0], key[1], key[2], key[3]
    new_doc = []
    for s in docs[key]:
      if idxs_counter[s] < args.threshold:
        replaced[s] += 1
        new_doc.append(unk)
        new_vocab.add(unk)        
      else:
        if s not in new_idxs_map:
          new_idxs_map[s] = new_idx
          new_idx += 1
        new_doc.append(new_idxs_map[s])
        new_vocab.add(new_idxs_map[s])
    new_idxs_as_str = ' '.join([str(i) for i in new_doc])
    of.write('%s %s %s %s %s\n' % (did, gid, fid, label, new_idxs_as_str))
  
  print len(replaced)
  print len(new_vocab)

if __name__ == '__main__':
  main()  