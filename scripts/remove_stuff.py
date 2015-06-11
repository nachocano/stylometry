from __future__ import division
import argparse
import os
import shutil

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-rif', '--raw_input_folder', required=True)
  args = parser.parse_args()

  genres = {'Adventure_Stories' : 1, 'Fiction' : 2, 'Historical_Fiction': 3, 'Love_Stories': 4, 'Mystery' : 5, 'Poetry' : 6, 'Science_Fiction' : 7, 'Short_Stories' : 8}
  labels = {'failure' : 0, 'success' : 1}

  changes = 0
  for genre in os.listdir(args.raw_input_folder):
    genre_folder_raw = os.path.join(args.raw_input_folder, genre)
    if not os.path.isdir(genre_folder_raw):
      continue
    gid = genres[genre]
    for fold in os.listdir(genre_folder_raw):
      fold_folder_raw = os.path.join(genre_folder_raw, fold)
      if not os.path.isdir(fold_folder_raw):
        continue
      fid = fold[-1]
      for fail_success in os.listdir(fold_folder_raw):
        fail_success_folder_raw = os.path.join(fold_folder_raw, fail_success)
        if not os.path.isdir(fail_success_folder_raw):
          continue
        label = labels[fail_success[:-1]]
        for document in os.listdir(fail_success_folder_raw):
          d_raw = os.path.join(fail_success_folder_raw, document)
          print 'processing document %s' % d_raw
          d_tmp = os.path.join(fail_success_folder_raw, document + ".tmp")
          tmp = open(d_tmp, 'w')
          if os.path.isfile(d_raw) and not d_raw.startswith('.'):
            did = document[:document.find('.')] # removing extension
            with open(d_raw) as f1:
              for l_raw in f1:
                line = l_raw.strip()
                if len(line) == 0:
                  continue
                line = line.lower()
                #if line.startswith('book') or line.startswith('chapter') or line.startswith('part'):
                #  changes += 1
                #  continue
                #if line.startswith('*') or line.startswith('..'):
                #  changes += 1
                #  continue
                #if 'decoration' in line or 'illustration' in line or 'sidenote' in line:
                #  changes += 1
                #  continue
                if len(line) == 1:
                  if line.startswith('i') or line.startswith('v') or line.startswith('x'):
                    changes += 1
                    continue
                  if line.startswith('1') or line.startswith('2') or line.startswith('3') or line.startswith('4'):
                    changes += 1
                    continue
                # if Love
                if gid == genres['Poetry']:
                  l = line.split()
                  last_elem = l[-1]
                  try:
                    x = int(last_elem)
                    line = ' '.join(str(e) for e in l[:-1])
                  except ValueError:
                    changes += 1
                    pass
                tmp.write('%s\n' % (line))
          tmp.close()
          
          shutil.copyfile(d_tmp, d_raw)
          os.remove(d_tmp)
          print 'changes so far %s' % changes
  print 'total changes %s' % changes

if __name__ == '__main__':
  main()
