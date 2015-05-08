from __future__ import division
import argparse
import time
import numpy as np
from gensim import models, utils
import logging

def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-i', '--input_file', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-d', '--dimension', required=False, type=int, default=100)
    parser.add_argument('-w', '--window', required=False, type=int, default=10)
    parser.add_argument('-mc', '--min_count', required=False, type=int, default=30)
    parser.add_argument('-s', '--sample', required=True, type=float, default=1e-3)
    parser.add_argument('-dm', '--dist_memory', required=False, type=int, default=0)
    parser.add_argument('-hs', '--hier_sampling', required=False, type=int, default=0)
    parser.add_argument('-n', '--negative', required=False, type=int, default=5)
    parser.add_argument('-it', '--iterations', required=True, type=int)

    args = parser.parse_args()

    begin = time.time()
    # should be two different input files
    train_sentences = build_sentences(args.input_file)
    
    start_alpha = 0.025
    model = models.Doc2Vec(size=args.dimension, alpha=start_alpha, window=args.window, min_count=args.min_count, sample=args.sample, 
        seed=1, workers=8, min_alpha=start_alpha, dm=args.dist_memory, hs=args.hier_sampling, negative=args.negative, dm_mean=1, train_words=True, train_lbls=True)
    logging.info('building vocab')
    start = time.time()
    model.build_vocab(train_sentences)
    logging.info('vocab built in %s' % (time.time() - start))

    for epoch in xrange(args.iterations):
        start = time.time()
        logging.info('training epoch %s with alpha %s' % (epoch, model.alpha))
        model.train(train_sentences)
        model.alpha = start_alpha * (1 / (epoch + 2))
        if model.alpha < start_alpha * 0.0001:
            model.alpha = start_alpha * 0.0001
        model.min_alpha = model.alpha
        elapsed = time.time() - start
        logging.info('epoch %s training took %s' % (epoch, elapsed))

    start = time.time()
    logging.info('saving model')
    model.save_word2vec_format(args.output_file, binary=False)
    elapsed = time.time() - start
    logging.info('model saved, took %s' % elapsed)

    total_time = time.time() - begin
    logging.info('overall run took %s' % total_time)
    
def build_sentences(input_file):
    logging.info('building sentences')
    build_start = time.time()
    sentences = []
    for line in open(input_file).read().splitlines():
        line = utils.to_unicode(line)
        line_splitted = line.split(' ')
        words = line_splitted[2:]
        # two labels (SENT and SYN)
        labels = [line_splitted[0], line_splitted[1]]
        sentences.append(models.doc2vec.LabeledSentence(words, labels))
    logging.info('sentences built, took %s' % (time.time() - build_start))
    return sentences

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logging.info("running doc2vec")
    main()

