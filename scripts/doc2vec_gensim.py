import argparse
import time
import numpy as np
from gensim import models, utils
import logging

def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-i', '--input_file', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-d', '--dimension', required=True, type=int)
    parser.add_argument('-w', '--window', required=True, type=int)
    parser.add_argument('-mc', '--min_count', required=True, type=int)
    parser.add_argument('-s', '--sample', required=True, type=float)
    parser.add_argument('-dm', '--dist_memory', required=True, type=int)
    parser.add_argument('-hs', '--hier_sampling', required=True, type=int)
    parser.add_argument('-n', '--negative', required=True, type=int)
    parser.add_argument('-it', '--iterations', required=True, type=int)

    args = parser.parse_args()

    begin = time.time()
    # should be two different input files
    train_sentences = build_sentences(args.input_file)
    
    start_alpha = 0.025
    model = models.Doc2Vec(size=args.dimension, alpha=start_alpha, window=args.window, min_count=args.min_count, sample=args.sample, 
        seed=1, workers=8, min_alpha=start_alpha, dm=args.dist_memory, hs=args.hier_sampling, negative=args.negative, dm_mean=0, train_words=True, train_lbls=True)
    logging.info('building vocab')
    start = time.time()
    model.build_vocab(train_sentences)
    logging.info('vocab built in %s' % (time.time() - start))

    for epoch in xrange(args.iterations):
        start = time.time()
        logging.info('training epoch %s with alpha %s' % (epoch, model.alpha))
        model.train(train_sentences)
        model.alpha -= 0.002
        if model.alpha < start_alpha * 0.0001:
            model.alpha = start_alpha * 0.0001
        model.min_alpha = model.alpha
        elapsed = time.time() - start
        logging.info('epoch %s training took %s' % (epoch, elapsed))

    model.save(args.output_file)
    # save it in the other format as well
    model.save_word2vec_format(args.output_file + '.w2v.txt', binary=False)

    total_time = time.time() - begin
    logging.info('overall run took %s' % total_time)
    
    # need to build the test sentences
    # test_sentences = build_sentences(args.input_file)
    #n_sentences = add_new_labels(test_sentences, model)
 
    # add new rows to model.syn0
    #n = model.syn0.shape[0]
    #model.syn0 = numpy.vstack((
    #    model.syn0,
    #    numpy.empty((n_sentences, model.layer1_size), dtype=numpy.float32)
    #))
 
    #for i in xrange(n, n + n_sentences):
        #numpy.random.seed(
        #    numpy.uint32(model.hashfxn(model.index2word[i] + str(model.seed))))
        #a = (numpy.random.rand(model.layer1_size) - 0.5) / model.layer1_size
        #model.syn0[i] = a
 
    # Set model.train_words to False and model.train_labels to True
    #model.train_words = False
    #model.train_lbls = True
 
    # train again just for test sentences
    #model.train(test_sentences)

def build_sentences(input_file):
    print 'building sentences'
    build_start = time.time()
    sentences = []
    for line in open(input_file).read().splitlines():
        line = utils.to_unicode(line)
        line_splitted = line.split(' ')
        words = line_splitted[1:]
        # single label
        label = [line_splitted[0]]
        sentences.append(models.doc2vec.LabeledSentence(words, label))
    logging.info('sentences built, took %s' % (time.time() - build_start))
    return sentences


# new labels to self.vocab
def add_new_labels(sentences, model):
    sentence_no = -1
    total_words = 0
    vocab = model.vocab
    model_sentence_n = len([l for l in vocab if l.startswith("SENT")])
    n_sentences = 0
    for sentence_no, sentence in enumerate(sentences):
        sentence_length = len(sentence.words)
        for label in sentence.labels:
            label_e = label.split("_")
            label_n = int(label_e[1]) + model_sentence_n
            label = "{0}_{1}".format(label_e[0], label_n)
            total_words += 1
            if label in vocab:
                vocab[label].count += sentence_length
            else:
                vocab[label] = gensim.models.word2vec.Vocab(
                    count=sentence_length)
                vocab[label].index = len(model.vocab)
                vocab[label].code = [0]
                vocab[label].sample_probability = 1.
                model.index2word.append(label)
                n_sentences += 1
    return n_sentences

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logging.info("running doc2vec")
    main()

