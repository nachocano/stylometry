import argparse
import time
import numpy as np
from gensim import models, utils
import logging
from collections import defaultdict

def contextwin(l, win):
    '''
    win :: int corresponding to the size of the window
    given a list of indexes composing a sentence
    it will return a list of list of indexes corresponding
    to context windows surrounding each word in the sentence
    '''
    assert (win % 2) == 1
    assert win >=1
    l = list(l)

    lpadded = win/2 * [-1] + l + win/2 * [-1]
    out = [ lpadded[i:i+win] for i in range(len(l)) ]

    assert len(out) == len(l)
    return out

def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-i', '--input_file', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-d', '--dimension', required=False, type=int, default=100)
    parser.add_argument('-lw', '--local_window', required=False, type=int, default=10)
    parser.add_argument('-gw', '--global_window', required=False, type=int, default=10)
    parser.add_argument('-mc', '--min_count', required=False, type=int, default=1)
    parser.add_argument('-s', '--sample', required=False, type=float, default=0)
    parser.add_argument('-dm', '--dist_memory', required=False, type=int, default=0)
    parser.add_argument('-hs', '--hier_sampling', required=False, type=int, default=0)
    parser.add_argument('-n', '--negative', required=False, type=int, default=5)
    parser.add_argument('-it', '--iterations', required=False, type=int, default=5)
    parser.add_argument('-t', '--workers', required=False, type=int, default=8)

    args = parser.parse_args()

    begin = time.time()
    # should be two different input files
    train_sentences = build_sentences(args.input_file, args.global_window)
    
    start_alpha = 0.025
    model = models.Doc2Vec(sentences=train_sentences, size=args.dimension, alpha=start_alpha, window=args.local_window, min_count=args.min_count, sample=args.sample, 
        seed=37, workers=args.workers, min_alpha=start_alpha, dm=args.dist_memory, hs=args.hier_sampling, negative=args.negative, dm_mean=1, 
        train_words=True, train_lbls=True, iter= args.iterations, gwindow=args.global_window)

#    for epoch in xrange(args.iterations):
#        start = time.time()
#        logging.info('********* training epoch %s with alpha %s ***' % (epoch, model.alpha))
#        model.train(train_sentences)
#        model.alpha = start_alpha * (1 / (epoch + 2))
#        if model.alpha < start_alpha * 0.0001:
#            model.alpha = start_alpha * 0.0001
#        model.min_alpha = model.alpha
#        elapsed = time.time() - start
#        logging.info('********* epoch %s training took %s **********' % (epoch, elapsed))

    start = time.time()
    logging.info('saving model')
    model.save_word2vec_format(args.output_file, binary=False)
    elapsed = time.time() - start
    logging.info('model saved, took %s' % elapsed)

    total_time = time.time() - begin
    logging.info('overall run took %s' % total_time)
    
def build_sentences(input_file, global_window):
    logging.info('building sentences')
    data = defaultdict(list)
    syn_idx = 0
    syn2idx = {}
    idx2syn = {}
    count = 0
    tick = time.time()
    for line in open(input_file).read().splitlines():
        if line == '':
            continue
        line = utils.to_unicode(line)
        line_splitted = line.split(' ')
        sentence = line_splitted[0]
        _, did, gid, fid, label, sentence_nr = sentence.split('_')
        syntax = line_splitted[1]
        words = line_splitted[2:]
        if syntax not in syn2idx:
            syn2idx[syntax] = syn_idx
            idx2syn[syn_idx] = syntax
            syn_idx += 1
        logging.info(count)
        count += 1
        data[(did, gid, fid, label)].append((int(sentence_nr), syn2idx[syntax], words))
    elapsed = time.time() - tick
    logging.info('read file, took %s' % elapsed)
    tick = time.time()
    logging.info('reading contexts')
    contexts = defaultdict(lambda : defaultdict(list))
    for k,v in data.iteritems():
        syns = []
        for e in v:
            syns.append(e[1])
        syns_arrays = contextwin(syns, global_window)
        print syns_arrays
        for array in syns_arrays:
            mid = int(len(array)/2)
            w = idx2syn[array[mid]]
            for left in array[:mid]:
                if left == -1:
                    continue
                contexts[k][w].append(idx2syn[left])
            for right in array[mid+1:]:
                if right == -1:
                    continue
                contexts[k][w].append(idx2syn[right])
    elapsed = time.time() - tick
    logging.info('read contexts, took %s' % elapsed)
    logging.info('building sentences')
    tick = time.time()
    sentences = []
    for k, v in data.iteritems():
        for i, elem in enumerate(v):
            label = 'SENT_%s_%s_%s_%s_%s' % (k[0], k[1], k[2], k[3], elem[0])
            syn = idx2syn[elem[1]]
            syn_cxts = []
            for sv in contexts[k][syn]:
                syn_cxts.append(sv)
            syntax = models.doc2vec.Syntax(syn, syn_cxts)
            sentence = models.doc2vec.LabeledSyntaxSentence(elem[2], [label], [syntax])
            sentences.append(sentence)
    elapsed = time.time() - tick
    logging.info('sentences built, took %s' % elapsed)
    return sentences

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logging.info("running doc2vec")
    main()

