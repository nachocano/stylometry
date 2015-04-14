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
        current_fold = cxt[i,2]
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

def update_fold_results(cxt_test, y_test, predictions):
    values = defaultdict(lambda : defaultdict(int))
    for i in xrange(y_test.shape[0]):
        key = utils.genres_dict[int(cxt_test[i,1])]
        if predictions[i] == y_test[i]:
            if predictions[i] == 1:
                values[key]['TP'] += 1
            else: 
                values[key]['TN'] += 1
        else:
            if predictions[i] == 1 and y_test[i] == 0:
                values[key]['FP'] += 1
            else:
                values[key]['FN'] += 1

    total_count = 0
    result = {}
    for gen in utils.genres_dict.itervalues():
        total_count += values[gen]['TP'] + values[gen]['TN'] + values[gen]['FP'] + values[gen]['FN']
        prec = utils.get_precision(values[gen]['TP'], values[gen]['FP'])
        rec = utils.get_recall(values[gen]['TP'], values[gen]['FN'])
        f1 = utils.get_f1(prec, rec)
        acc = utils.get_accuracy(values[gen]['TP'], values[gen]['TN'], values[gen]['FP'], values[gen]['FN'])
        result[gen] = (prec, rec, f1, acc)
    assert total_count == y_test.shape[0], "invalid total count %d, should be %d" % (total_count, y_test.shape[0])
    return result

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-c', '--classifier', required=True)
    args = parser.parse_args()

    begin = time.time()

    data = np.genfromtxt(args.input)
    # doc id, gender id, fold id
    cxt = data[:,:3]
    y = data[:,3]
    x = data[:,4:]

    x = utils.to_multitask(x, cxt[:,1])

    parameters = utils.build_parameters(args.classifier)
    folds = np.unique(cxt[:,2])
    # divide train and test based on fold 
    results = {}
    for fold in folds:
        print 'executing fold %d ----' % int(fold)
        x_train, y_train, cxt_train, x_test, y_test, cxt_test = build_data(x, y, cxt, fold)
        best_f1 = 0.0
        best_params = None
        best_p = 0.0
        best_r = 0.0
        results[int(fold)] = {}
        for params in parameters:
            print 'param %s' % params
            clf = utils.create_classifier(args.classifier, params)
            predictions = utils.execute(clf, x_train, y_train, x_test)
            p, r, f1 = utils.evaluate(y_test, predictions)
            if best_f1 < f1:
                print 'updating best results for fold %s' % fold
                best_params = params
                best_p = p
                best_r = r
                best_f1 = f1
                results[int(fold)] = update_fold_results(cxt_test, y_test, predictions)

    print 'computing averages results'
    avg_results = defaultdict(lambda: defaultdict(int))
    for result in results:
        result_per_fold = results[result]
        for gen in result_per_fold:
            p,r,f1, acc = result_per_fold[gen]
            avg_results[gen]['P'] += p
            avg_results[gen]['R'] += r
            avg_results[gen]['F'] += f1
            avg_results[gen]['A'] += acc

    for gen in avg_results:
        avg_results[gen]['P'] /= len(folds)
        avg_results[gen]['R'] /= len(folds)
        avg_results[gen]['F'] /= len(folds)
        avg_results[gen]['A'] /= len(folds)


    print 'writing output file'
    out = open(args.output, "w")
    for gen in avg_results:
        out.write('%s,%s,%s,%s,%s\n' % (gen, avg_results[gen]['P'], avg_results[gen]['R'], avg_results[gen]['F'], avg_results[gen]['A']))
    out.close()

    elapsed_run = time.time() - begin
    print 'all run took %s' % elapsed_run



if __name__ == '__main__':
  main()
