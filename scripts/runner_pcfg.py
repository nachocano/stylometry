import argparse
import os

def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-i', '--input_dir', required=True)
  parser.add_argument('-o', '--output_dir', required=True)
  parser.add_argument('-j', '--jar_file', required=True)
  args = parser.parse_args()

  print 'running %s' % input_dir
  cmd = 'nohup java -Xmx512m -jar %s -i %s -o %s' % (args.jar_file, args.input_dir, args.output_dir)
  print cmd
  os.system(cmd)

if __name__ == '__main__':
  main()