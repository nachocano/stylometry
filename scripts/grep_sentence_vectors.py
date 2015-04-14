from __future__ import division
import argparse
import re

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--input_file', required=True)
  args = parser.parse_args()

  p = re.compile(ur'^SENT_(\d+)_(\d)_(\d)_(\d)$')
  for line in open(args.input_file).read().splitlines():
    l = line.split()
    search_obj = re.search(p, l[0])
    if search_obj:
      did = search_obj.group(1)
      gid = search_obj.group(2)
      fid = search_obj.group(3)
      label = search_obj.group(4)
      l_as_str = ' '.join(v for v in l[1:])
      print '%s %s %s %s %s' % (did, gid, fid, label, l_as_str)
      
if __name__ == '__main__':
  main()
