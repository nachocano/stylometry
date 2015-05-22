from sklearn.externals import joblib
from sklearn import ensemble
from sklearn import linear_model
from sklearn import svm
from sklearn.metrics import precision_recall_fscore_support
from sklearn import cross_validation
import numpy as np
import time
from collections import defaultdict
from sklearn.metrics import accuracy_score
import os
from itertools import groupby
import random

genres_dict = {1 : 'Adventure_Stories', 2: 'Fiction' , 3: 'Historical_Fiction', 4: 'Love_Stories', 5: 'Mystery', 6: 'Poetry', 7: 'Science_Fiction', 8: 'Short_Stories'}
genres = {'Adventure_Stories' : 1, 'Fiction' : 2, 'Historical_Fiction': 3, 'Love_Stories': 4, 'Mystery' : 5, 'Poetry' : 6, 'Science_Fiction' : 7, 'Short_Stories' : 8}
novel_labels = {'failure' : 0, 'success' : 1}

def save_model(filename, model):
  if filename:
    print 'saving model to %s' % filename
    joblib.dump(model, filename)
    print 'model saved to %s' % filename

def load_model(filename):
  print 'loading model from %s' % filename
  clf = joblib.load(filename)
  print 'model loaded from %s' % filename
  return clf

def get_precision(TP, FP):
    if (TP+FP) > 0:
        precision = float(TP) / (TP + FP)
        return precision
    else:
        return 0.0

def get_recall(TP, FN):
    if (TP+FN) > 0:
        recall = float(TP) / (TP + FN)
        return recall
    else:
        return 0.0

def get_f1(precision=None, recall=None):
    if precision + recall > 0:
        return float(2 * precision * recall) / (precision + recall)
    else:
        return 0.0

def get_accuracy(TP, TN, FP, FN):
    return float(TP + TN) / (TP + FP + FN + TN)

def create_classifier(classifier, params):
    if classifier == 'tree':
        estimators, depth = params.split(',')
        return ensemble.ExtraTreesClassifier(n_estimators=int(estimators), max_depth=int(depth), random_state=37)
    elif classifier == 'lr':
        C = float(params)
        return linear_model.LogisticRegression(C=C, penalty='l2')
    elif classifier == 'svm':
        C = float(params)
        return svm.SVC(C=C)
    else:
        print 'unsupported classifier %s' % classifier
        exit(1)

def error(y_truth, y_pred):
    n = y_truth.shape[0]
    mismatches = 0
    for i, value in enumerate(y_truth):
        if y_pred[i] != value:
            mismatches += 1
    return float(mismatches)/n

def rmse(y_truth, y_pred):
    n = y_truth.shape[0]
    return np.sqrt(1./n * np.sum((y_truth - y_pred)**2))
    
def train(model, x, y):
    begin = time.time()
    #print 'training classifier'
    m = model.fit(x, y)
    elapsed_run = time.time() - begin
    #print 'training took %s' % elapsed_run
    return m

def test(model, x):
    begin = time.time()
    #print 'testing classifier'
    pred = model.predict(x)
    elapsed_run = time.time() - begin
    #print 'testing took %s' % elapsed_run
    return pred

def evaluate(y_truth, y_pred):
    precision, recall, f1, _ = precision_recall_fscore_support(y_truth, y_pred, average='micro')
    accuracy = accuracy_score(y_truth, y_pred)
    return precision, recall, f1, accuracy

def execute(clf, x_train, y_train, x_test):
    clf = train(clf, x_train, y_train)
    return test(clf, x_test)

def build_parameters(classifier):
    parameters = []
    if classifier == 'tree':
        estimators = [10, 20, 50, 100, 150, 200]
        depths = [10, 20, 50, 100, 150, 200]
        for estimator in estimators:
            for depth in depths:
                parameters.append('%s,%s' % (estimator, depth))
    elif classifier == 'lr' or classifier == 'svm':
        Cs = [0.1, 0.3, 0.5, 1.0, 2.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0]
        parameters.extend(Cs)
    else:
        print 'unsupported classifier %s' % classifier
        exit(1)
    return parameters

def to_multitask(x, cxt):
    genres = len(np.unique(cxt))
    added_columns = x.shape[1] * genres
    rest = np.zeros([x.shape[0], added_columns])
    for i in xrange(x.shape[0]):
        genreid = int(cxt[i])
        # genre id starts from 1, but this is a new array, start from zero
        start = x.shape[1] * (genreid - 1)
        end = start + x.shape[1]
        rest[i][start:end] = x[i]
    new_x = np.hstack((x, rest))
    return new_x

def update_fold_results(y_test, predictions):
    values = defaultdict(int)
    for i in xrange(y_test.shape[0]):
        if predictions[i] == y_test[i]:
            if predictions[i] == 1:
                values['TP'] += 1
            else: 
                values['TN'] += 1
        else:
            if predictions[i] == 1 and y_test[i] == 0:
                values['FP'] += 1
            else:
                values['FN'] += 1

    total_count = values['TP'] + values['TN'] + values['FP'] + values['FN']
    assert total_count == y_test.shape[0], "invalid total count %d, should be %d" % (total_count, y_test.shape[0])
    prec = get_precision(values['TP'], values['FP'])
    rec = get_recall(values['TP'], values['FN'])
    f1 = get_f1(prec, rec)
    acc = get_accuracy(values['TP'], values['TN'], values['FP'], values['FN'])
    return (prec, rec, f1, acc)    

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


def read_data(raw, parsed, corpus):
    data = read_raw_novels(raw) if corpus == 'novels' else read_raw_nyt(raw)
    syn_data = read_syn_novels(parsed) if corpus == 'novels' else read_syn_nyt(parsed)
    for d, s in zip(data[0], syn_data[0]):
        assert d[0] == s[0]
    return data, syn_data

def read_raw_nyt(folder):
    print 'TODO'
    exit()

def read_syn_nyt(folder):
    print 'TODO'
    exit()

def read_novels(folder, get_sentence):
    words2idx = {}
    word_idx = 0
    novels = []
    for genre in os.listdir(folder):
        genre_folder = os.path.join(folder, genre)
        if not os.path.isdir(genre_folder):
            continue
        gid = genres[genre]
        for fold in os.listdir(genre_folder):
            fold_folder = os.path.join(genre_folder, fold)
            if not os.path.isdir(fold_folder):
                continue
            fid = fold[-1]
            for fail_success in os.listdir(fold_folder):
                fail_success_folder = os.path.join(fold_folder, fail_success)
                if not os.path.isdir(fail_success_folder):
                    continue
                label = novel_labels[fail_success[:-1]]
                for document in os.listdir(fail_success_folder):
                    d = os.path.join(fail_success_folder, document)
                    if os.path.isfile(d) and not d.startswith('.'):
                        did = document[:document.find('.')] # removing extension
                        sentences = []
                        for line in open(d).read().splitlines():
                            word_idx, sentence = get_sentence(line, words2idx, word_idx)
                            sentences.append(sentence)
                        novels.append(((did, gid, fid, label), sentences))
    assert len(novels) == 800
    return novels, words2idx 

# can use this one if I use NP VP ., instead of the SYN version
def get_sentence(line, dictionary, idx):
    words = line.split()
    sentence = []
    for w in words:
        # convert to lowercase
        w = w.lower()
        if w not in dictionary:
            dictionary[w] = idx
            idx += 1
        sentence.append(dictionary[w])
    return idx, np.asarray(sentence).astype('int32')

def read_raw_novels(folder):
    return read_novels(folder, get_sentence)

def read_syn_novels(folder):
    # use this one when changing the parsed to SYN_i, instead of the whole parse
    def get_sentence(line, dictionary, idx):
        parsed = line.strip()
        if parsed not in dictionary:
            # right now we are using the same indexes for syns and regular words. 
            # should probably change it
            dictionary[parsed] = idx
            idx += 1
        return idx, dictionary[parsed]
    
    return read_novels(folder, get_sentence)

def shuffle(lol, seed):
    '''
    lol :: list of list as input
    seed :: seed the shuffling

    shuffle inplace each list in the same order
    '''
    for l in lol:
        random.seed(seed)
        random.shuffle(l)    

