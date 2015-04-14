from sklearn.externals import joblib
from sklearn import ensemble
from sklearn import linear_model
from sklearn import svm
from sklearn.metrics import precision_recall_fscore_support
from sklearn import cross_validation
import numpy as np
import time
from collections import defaultdict

genres_dict = {1 : 'Adventure_Stories', 2: 'Fiction' , 3: 'Historical_Fiction', 4: 'Love_Stories', 5: 'Mystery', 6: 'Poetry', 7: 'Science_Fiction', 8: 'Short_Stories'}

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
        return linear_model.LogisticRegression(C=C)
    elif classifier == 'svm':
        C = float(params)
        return svm.SVC(C=C)
    else:
        print 'unsupported classifier %s' % classifier
        exit(1)
    
def train(model, x, y):
    begin = time.time()
    print 'training classifier'
    m = model.fit(x, y)
    elapsed_run = time.time() - begin
    print 'training took %s' % elapsed_run
    return m

def test(model, x):
    begin = time.time()
    print 'testing classifier'
    pred = model.predict(x)
    elapsed_run = time.time() - begin
    print 'testing took %s' % elapsed_run
    return pred

def evaluate(y_truth, y_pred):
    precision, recall, f1, _ = precision_recall_fscore_support(y_truth, y_pred, average='micro')
    return precision, recall, f1

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
        Cs = [0.1, 0.3, 0.5, 1.0, 2.0, 10.0, 100.0, 1000.0]
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
