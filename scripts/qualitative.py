from __future__ import division
import argparse
import numpy as np
import os
from gensim.models import word2vec
from collections import Counter
import time
import matplotlib.pyplot as plt

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-iv', '--input_vocab', required=True)
  parser.add_argument('-ir', '--input_raw', required=True)
  parser.add_argument('-n', '--number_items', required=False, type=int, default=10)

  args = parser.parse_args()

  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=False)
  model.init_sims()
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed

  syn_dictionary = {}
  for line in open(args.input_vocab).read().splitlines():
    syn_name, syn = line.split('\t')
    syn_dictionary[syn_name] = syn

  raw_dictionary = {}
  counts = Counter()
  for line in open(args.input_raw).read().splitlines():
    syn_name, raw_sentences = line.split('\t')
    splitted = raw_sentences.split('|^^|')
    raw_dictionary[syn_name] = splitted
    counts[syn_name] += len(splitted)

  # most common syntaxes
  most_common = [m[0] for m in counts.most_common(args.number_items)]

  # most similar to the most common syntax
  most_similar = [m[0] for m in model.most_similar(positive = counts.most_common(1)[0][0])]

  svd_plot(model, most_common, lambda i, k : most_common[i])
  svd_plot(model, most_similar, lambda i, k : syn_dictionary[k])

def svd_plot(model, keys, fc):
  vectors = []
  for syntax_name in keys:
    vectors.append(model.syn0[model.vocab[syntax_name].index])
  vectors = np.array(vectors)
  temp = vectors - np.mean(vectors, axis=0)
  covariance = 1.0 / len(keys) * temp.T.dot(temp)
  U,S,V = np.linalg.svd(covariance)
  coord = temp.dot(U[:,0:2])
  for i in xrange(len(keys)):
    plt.text(coord[i,0], coord[i,1], fc(i, keys[i]), bbox=dict(facecolor='green', alpha=0.1))
  plt.xlim((np.min(coord[:,0]), np.max(coord[:,0])))
  plt.ylim((np.min(coord[:,1]), np.max(coord[:,1])))
  plt.show()  





'''
"_, wordVectors0, _ = load_saved_params()\n",
"wordVectors = (wordVectors0[:nWords,:] + wordVectors0[nWords:,:])\n",
"visualizeWords = [\"the\", \"a\", \"an\", \",\", \".\", \"?\", \"!\", \"``\", \"''\", \"--\", \"good\", \"great\", \"cool\", \"brilliant\", \"wonderful\", \"well\", \"amazing\", \"worth\", \"sweet\", \"enjoyable\", \"boring\", \"bad\", \"waste\", \"dumb\", \"annoying\"]\n",
"visualizeIdx = [tokens[word] for word in visualizeWords]\n",
"visualizeVecs = wordVectors[visualizeIdx, :]\n",
"temp = (visualizeVecs - np.mean(visualizeVecs, axis=0))\n",
"covariance = 1.0 / len(visualizeIdx) * temp.T.dot(temp)\n",
"U,S,V = np.linalg.svd(covariance)\n",
"coord = temp.dot(U[:,0:2]) \n",
"\n",
"for i in xrange(len(visualizeWords)):\n",
"    plt.text(coord[i,0], coord[i,1], visualizeWords[i], bbox=dict(facecolor='green', alpha=0.1))\n",
"    \n",
"plt.xlim((np.min(coord[:,0]), np.max(coord[:,0])))\n",
"plt.ylim((np.min(coord[:,1]), np.max(coord[:,1])))"
]
},
'''

if __name__ == '__main__':
  main()
