from __future__ import division
import time
import argparse
import numpy as np
from collections import defaultdict
import utils
from copy import deepcopy

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

def rmse_per_genre(cxt_test, y_test, predictions):
    values = defaultdict(lambda : defaultdict(list))
    for i in xrange(y_test.shape[0]):
        key = utils.genres_dict[int(cxt_test[i,1])]
        values[key]['truth'].append(y_test[i])
        values[key]['pred'].append(predictions[i])

    result = {}
    for gen in utils.genres_dict.itervalues():
        assert len(values[gen]['truth']) == len(values[gen]['pred'])
        rmse = utils.rmse(np.array(values[gen]['truth']), np.array(values[gen]['pred']))
        result[gen] = rmse
    return result

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

    #x = utils.to_multitask(x, cxt[:,1])

    parameters = utils.build_parameters(args.classifier)
    folds = np.unique(cxt[:,2]).astype(int)
    # divide train and test based on fold 
    results_per_test_fold = {}
    for test_fold in folds:
        results_per_test_fold[int(test_fold)] = {}
        print 'executing test fold %d' % int(test_fold)
        x_train_all, y_train_all, cxt_train_all, x_test, y_test, cxt_test = build_data(x, y, cxt, test_fold)
        train_folds = set(folds) - set([test_fold])
        results_per_val_fold = {}
        for val_fold in train_folds:
            print ' executing val fold %d' % int(val_fold)
            results_per_val_fold[int(val_fold)] = {}
            x_train, y_train, cxt_train, x_val, y_val, cxt_val = build_data(x_train_all, y_train_all, cxt_train_all, val_fold)
            best_rmses = {}
            best_clfs = {}
            for params in parameters:
                print '  tunning with param %s' % params
                clf = utils.create_classifier(args.classifier, params)
                predictions = utils.execute(clf, x_train, y_train, x_val)
                p_results = rmse_per_genre(cxt_val, y_val, predictions)
                for genre in p_results:
                    rmse_genre = p_results[genre]
                    if genre not in best_rmses:
                        best_rmses[genre] = float('inf')
                    if rmse_genre < best_rmses[genre]:
                        print '   updating best result for genre %s for val fold %s, %s' % (genre, val_fold, rmse_genre)
                        best_rmses[genre] = rmse_genre
                        best_clfs[genre] = deepcopy(clf)
                    else:
                        print '   not updating best result for genre %s for val fold %s, %s' % (genre, val_fold, rmse_genre)
            for genre in best_clfs:
                clf = best_clfs[genre]
                predictions = utils.test(clf, x_test)
                rmse = utils.rmse(y_test, predictions)
                p_results = update_fold_results(cxt_test, y_test, predictions)
                results_per_val_fold[int(val_fold)][genre] = p_results[genre]
                print '  testing on val fold %d, acc %s for genre %s, rmse %s' % (int(val_fold), p_results[genre][3], genre, rmse)
        
        print ' computing averages of train folds %s for test fold %s' % (train_folds, int(test_fold))
        avg_results = defaultdict(lambda: defaultdict(int))
        for vf in results_per_val_fold:
            res = results_per_val_fold[vf]
            for gen in res:
                p,r,f1,acc = res[gen]
                avg_results[gen]['P'] += p
                avg_results[gen]['R'] += r
                avg_results[gen]['F'] += f1
                avg_results[gen]['A'] += acc
        for gen in avg_results:
            avg_results[gen]['P'] /= len(train_folds)
            avg_results[gen]['R'] /= len(train_folds)
            avg_results[gen]['F'] /= len(train_folds)
            avg_results[gen]['A'] /= len(train_folds)
        
        results_per_test_fold[int(test_fold)] = avg_results


    print 'computing overall averages results'
    averages = defaultdict(lambda: defaultdict(int))
    for tf in results_per_test_fold:
        avg = results_per_test_fold[tf]
        for gen in avg:
            averages[gen]['P'] += avg[gen]['P']
            averages[gen]['R'] += avg[gen]['R']
            averages[gen]['F'] += avg[gen]['F']
            averages[gen]['A'] += avg[gen]['A']

    avg_accuracy = 0
    for gen in averages:
        averages[gen]['P'] /= len(folds)
        averages[gen]['R'] /= len(folds)
        averages[gen]['F'] /= len(folds)
        averages[gen]['A'] /= len(folds)
        avg_accuracy += averages[gen]['A']
    avg_accuracy /= len(averages)


    print 'writing output file'
    out = open(args.output, "w")
    for gen in averages:
        out.write('%s,%s,%s,%s,%s\n' % (gen, averages[gen]['P'], averages[gen]['R'], averages[gen]['F'], averages[gen]['A']))
    out.write('accuracy avg: %s\n' % avg_accuracy)
    out.close()

    elapsed_run = time.time() - begin
    print 'all run took %s' % elapsed_run



if __name__ == '__main__':
  main()
