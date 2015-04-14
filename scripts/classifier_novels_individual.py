from __future__ import division
import time
import argparse
import numpy as np
from collections import defaultdict
import utils


def build_data(x, y, cxt, test_fold):
    x_train_list = defaultdict(list)
    y_train_list = defaultdict(list)
    cxt_train_list = defaultdict(list)
    x_test_list = defaultdict(list)
    y_test_list = defaultdict(list)
    cxt_test_list = defaultdict(list)
    for i in xrange(x.shape[0]):
        gen = utils.genres_dict[int(cxt[i,1])]
        current_fold = cxt[i,2]
        if current_fold == test_fold:
            cxt_test_list[gen].append(cxt[i])
            x_test_list[gen].append(x[i])
            y_test_list[gen].append(y[i])            
        else:
            cxt_train_list[gen].append(cxt[i])
            x_train_list[gen].append(x[i])
            y_train_list[gen].append(y[i])
    x_train = {}
    y_train = {}
    cxt_train = {}
    x_test = {}
    y_test = {}
    cxt_test = {}
    for gen in x_train_list:
        x_train[gen] = np.array(x_train_list[gen]).astype(np.float32)
        y_train[gen] = np.array(y_train_list[gen]).astype(int)
        cxt_train[gen] = np.array(cxt_train_list[gen]).astype(int)
        x_test[gen] = np.array(x_test_list[gen]).astype(np.float32)
        y_test[gen] = np.array(y_test_list[gen]).astype(int)
        cxt_test[gen] = np.array(cxt_test_list[gen]).astype(int)
    return x_train, y_train, cxt_train, x_test, y_test, cxt_test

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
    prec = utils.get_precision(values['TP'], values['FP'])
    rec = utils.get_recall(values['TP'], values['FN'])
    f1 = utils.get_f1(prec, rec)
    acc = utils.get_accuracy(values['TP'], values['TN'], values['FP'], values['FN'])
    return (prec, rec, f1, acc)


''' creates individual models for the different genres '''
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

    parameters = utils.build_parameters(args.classifier)
    folds = np.unique(cxt[:,2])
    # divide train and test based on fold and genre
    results = defaultdict(defaultdict)
    for fold in folds:
        print 'executing fold %d ----' % int(fold)
        x_train, y_train, cxt_train, x_test, y_test, cxt_test = build_data(x, y, cxt, fold)
        for gen in x_train:
            best_f1 = 0.0
            best_params = None
            best_p = 0.0
            best_r = 0.0
            for params in parameters:
                print 'param %s' % params
                clf = utils.create_classifier(args.classifier, params)
                predictions = utils.execute(clf, x_train[gen], y_train[gen], x_test[gen])
                p, r, f1 = utils.evaluate(y_test[gen], predictions)
                if best_f1 < f1:
                    print 'updating best results for fold %s, for gen %s' % (fold, gen)
                    best_params = params
                    best_p = p
                    best_r = r
                    best_f1 = f1
	            results[gen][int(fold)] = update_fold_results(y_test[gen], predictions)

    print 'computing averages results'
    avg_results = defaultdict(lambda: defaultdict(int))
    for result in results:
        result_per_gen = results[result]
        for fold in result_per_gen:
            p,r,f1,acc = result_per_gen[fold]
            avg_results[result]['P'] += p
            avg_results[result]['R'] += r
            avg_results[result]['F'] += f1
            avg_results[result]['A'] += acc

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
