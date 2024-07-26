import numpy as np
import pandas as pd
import sys
#sys.path.append('C:/Users/g.oudevrielink/Documents/Project/connection-prediction/code')
import model.decisiontree as decisiontree

def kFoldValidation(data,k,depth,trees):
    max_depth = depth
    number_trees = trees

    data = data.sample(frac=1).reset_index(drop=True)
    folds = np.array_split(data,k)
    total = 0

    for i in range(k):
        testSet = folds[i].reset_index(drop=True)
        trainSet = pd.concat(folds[:i]+folds[i + 1:]).reset_index(drop=True)
        tree = decisiontree.random_forest(trainSet,'Output', number_trees , True, max_depth, 5, 1e-5)
        prediction = decisiontree.rf_classifier(testSet,tree,'Output')
        total += prediction

    return total/k