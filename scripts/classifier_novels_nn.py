from __future__ import division
import time
import argparse
import numpy as np
from collections import defaultdict
import utils
import graphlab as gl


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
            cxt_test.append(cxt[i,2])
            x_test_list.append(x[i] * 255)
            y_test_list.append(y[i])            
        else:
            cxt_train.append(cxt[i,2])
            x_train_list.append(x[i] * 255)
            y_train_list.append(y[i])

    new_x_train_list = []
    new_x_test_list = []
    for elem in x_train_list:
        new_x_train_list.append([0 if x < 0 else x for x in elem])
    for elem in x_test_list:
        new_x_test_list.append([0 if x < 0 else x for x in elem])

    x_train = gl.SArray(new_x_train_list) 
    x_train = gl.SArray.pixel_array_to_image(x_train, 20, 20, 1, undefined_on_failure=False, allow_rounding=True)
    y_train = gl.SArray(y_train_list)
    cxt_train = gl.SArray(cxt_train)
    x_test = gl.SArray(new_x_test_list)
    x_test = gl.SArray.pixel_array_to_image(x_test, 20, 20, 1, undefined_on_failure=False, allow_rounding=True)
    y_test = gl.SArray(y_test_list)
    cxt_test = gl.SArray(cxt_test)

    train = gl.SFrame(data=x_train, format='sarray')
    train.add_column(y_train, name='label')
    test = gl.SFrame(data=x_test, format='sarray')
    test.add_column(y_test, name='label')
    cxt_train_sf = gl.SFrame(data=cxt_train, format='sarray')
    cxt_test_sf = gl.SFrame(data=cxt_test, format='sarray')
    cxt_train_sf.rename({'X1': 'genre'})
    cxt_test_sf.rename({'X1': 'genre'})
    return train, cxt_train_sf, test, cxt_test_sf

'''
def build_data(sf, test_fold):
    train_sf = sf[sf['fold'] != test_fold]
    train_sf.remove_columns(['id', 'genre', 'fold'])
    cxt_train_sf = sf[sf['fold'] != test_fold].select_columns(['id', 'genre', 'fold'])
    test_sf = sf[sf['fold'] == test_fold]
    test_sf.remove_columns(['id', 'genre', 'fold'])
    cxt_test_sf = sf[sf['fold'] == test_fold].select_columns(['id', 'genre', 'fold'])
    return train, cxt_train, test, cxt_test
'''

def update_fold_results(cxt_test, y_test, predictions):
    values = defaultdict(lambda : defaultdict(int))
    for i in xrange(y_test.size()):
        key = utils.genres_dict[cxt_test[i]]
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
    assert total_count == y_test.size(), "invalid total count %d, should be %d" % (total_count, y_test.size())
    return result

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()

    begin = time.time()

    #sf = gl.SFrame.read_csv(args.input, delimiter=' ', header=False, verbose=False)
    #sf.rename({'X1': 'id', 'X2':'genre', 'X3' : 'fold', 'X4' : 'label'})

    data = np.genfromtxt(args.input)
    # doc id, gender id, fold id
    cxt = data[:,:3]
    y = data[:,3].astype(int)
    x = data[:,4:]    

    #folds = np.unique(sf['fold'])
    folds = np.unique(cxt[:,2]).astype(int)
    # divide train and test based on fold
    results = {}
    for fold in folds:
        print 'executing fold %d ----' % int(fold)
        train, cxt_train, test, cxt_test = build_data(x, y, cxt, fold)
        #train, cxt_train, test, cxt_test = build_data(sf, fold)
        net = gl.deeplearning.create(train, 'label', network_type='auto')
        #net = gl.deeplearning.MultiLayerPerceptrons(1, [2], activation='sigmoid', init_random='random')
        net.params['batch_size'] = 100
        net = gl.deeplearning.ConvolutionNet(num_convolution_layers=1,
                                               kernel_size=3, stride=2,
                                               num_channels=1,
                                               num_output_units=2,
                                               pooling='max_pooling')
        '''
        net = gl.deeplearning.get_builtin_neuralnet('mnist')
        net.params['metric'] = 'accuracy'
        net.layers[6].num_hidden_units = 2
        '''
        print net.layers
        net.verify()
        # {sigmoid, tanh, relu, softplus}
        clf = gl.neuralnet_classifier.create(train, target='label', network = net, metric = 'accuracy', max_iterations=5000)
        predictions = clf.classify(test)
        p_results = update_fold_results(cxt_test['genre'], test['label'], predictions['class'])
        results[int(fold)] = {}
        for genre in p_results:
            results[int(fold)][genre] = p_results[genre]
        #break
               
    print 'computing averages results'
    avg_results = defaultdict(lambda: defaultdict(int))
    for result in results:
        result_per_fold = results[result]
        for gen in result_per_fold:
            p,r,f1,acc = result_per_fold[gen]
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
        print '%s,%s,%s,%s,%s\n' % (gen, avg_results[gen]['P'], avg_results[gen]['R'], avg_results[gen]['F'], avg_results[gen]['A'])
        out.write('%s,%s,%s,%s,%s\n' % (gen, avg_results[gen]['P'], avg_results[gen]['R'], avg_results[gen]['F'], avg_results[gen]['A']))
    out.close()

    elapsed_run = time.time() - begin
    print 'all run took %s' % elapsed_run

if __name__ == '__main__':
  main()
