from __future__ import division
import time
import argparse
import numpy as np
from collections import defaultdict
import utils

def build_data(x, y, cxt, test_fold):
    x_train_list = []
    y_train_list = []
    cxt_train = []
    x_test_list = []
    y_test_list = []
    cxt_test = []
    for i in xrange(x.shape[0]):
        current_fold = cxt[i,4]
        if current_fold == test_fold:
            cxt_test.append(cxt[i])
            x_test_list.append(x[i])
            y_test_list.append(y[i])
        else:
            cxt_train.append(cxt[i])
            x_train_list.append(x[i])
            y_train_list.append(y[i])

    x_train = np.array(x_train_list).astype(np.float32)
    y_train = np.array(y_train_list).astype(int)
    cxt_train = np.array(cxt_train).astype(int)
    x_test = np.array(x_test_list).astype(np.float32)
    y_test = np.array(y_test_list).astype(int)
    cxt_test = np.array(cxt_test).astype(int)
    return x_train, y_train, cxt_train, x_test, y_test, cxt_test    

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-v', '--validation', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-c', '--classifier', required=True)
    args = parser.parse_args()

    begin = time.time()

    data = np.genfromtxt(args.input)
    # year, month, day, identifier, fold, label, embedding
    # doc id, gender id, fold id
    cxt = data[:,:5].astype(int)
    y = data[:,5].astype(int)
    x = data[:,5:]

    # year, month, day, identifier, label, embedding
    validation = np.genfromtxt(args.validation)
    cxt_valid = validation[:,4].astype(int)
    y_valid = validation[:,4].astype(int)
    x_valid = validation[:,4:]

    parameters = utils.build_parameters(args.classifier)
    folds = np.unique(cxt[:,4])
    # divide train and test based on fold
    results = {}
    for fold in folds:
        print 'executing fold %d ----' % int(fold)
        x_train, y_train, cxt_train, x_test, y_test, cxt_test = build_data(x, y, cxt, fold)
        best_accuracies = defaultdict(int)
        clf_best = None
        # tunning model on validation data per fold
        for params in parameters:
            print 'param %s' % params
            clf = utils.create_classifier(args.classifier, params)
            predictions = utils.execute(clf, x_train, y_train, y_valid)
            p_results = utils.update_fold_results(y_valid, predictions)
            acc = p_results[3]
            if acc > best_accuracies[int(fold)]:
                print 'updating best results for fold %s' % fold
                best_accuracies[int(fold)] = acc
                clf_best = clf

        # now test on test data
        predictions = utils.test(clf_best, y_test)
        p_results = utils.update_fold_results(y_test, predictions)
        results[int(fold)] = p_results

    print 'computing averages results'
    avg_results = defaultdict(int)
    for result in results:
        p,r,f1,acc = results[result]
        avg_results['P'] += p
        avg_results['R'] += r
        avg_results['F'] += f1
        avg_results['A'] += acc

    avg_results['P'] /= len(folds)
    avg_results['R'] /= len(folds)
    avg_results['F'] /= len(folds)
    avg_results['A'] /= len(folds)

    print 'writing output file'
    out = open(args.output, "w")
    out.write('%s,%s,%s,%s\n' % (avg_results['P'], avg_results['R'], avg_results['F'], avg_results['A']))
    out.close()

    elapsed_run = time.time() - begin
    print 'all run took %s' % elapsed_run

if __name__ == '__main__':
  main()
