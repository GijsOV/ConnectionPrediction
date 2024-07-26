import pandas as pd
import numpy as np
import itertools
import random
import math

#Decision tree
#Functions
def gini_impurity(c):
  if isinstance(c, pd.Series):
    p = c.value_counts()/c.shape[0]
    gini = 1-np.sum(c**2)
    return(gini) 
  else:
    raise('Object must be a Pandas Series.')

def entropy(c):
  if isinstance(c, pd.Series):
    p = c.value_counts()/c.shape[0]
    entropy = np.sum(-p*np.log2(p+1e-9))
    return(entropy)
  else:
    raise('Object must be a Pandas Series.')  

def variance(y):
  if(len(y) == 1):
    return 0
  else:
    return y.var()

def information_gain(y, mask, func=entropy):
  a = sum(mask)
  b = mask.shape[0] - a
  if(a == 0 or b ==0): 
    ig = 0
  else:
    if y.dtypes != 'O':
      ig = variance(y) - (a/(a+b)* variance(y[mask])) - (b/(a+b)*variance(y[-mask]))
    else:
      ig = func(y)-a/(a+b)*func(y[mask])-b/(a+b)*func(y[-mask])
  return ig



#Split operations
def categorical_options(a):
  a = a.unique()
  opciones = []
  for L in range(0, len(a)+1):
      for subset in itertools.combinations(a, L):
          subset = list(subset)
          opciones.append(subset)
  return opciones[1:-1]

def max_information_gain_split(x, y, func=entropy):
  split_value = []
  ig = [] 
  numeric_variable = True if x.dtypes != 'O' else False

  if numeric_variable:
    options = x.sort_values().unique()[1:]
  else: 
    options = categorical_options(x)

  for val in options:
    mask =   x < val if numeric_variable else x.isin(val)
    val_ig = information_gain(y, mask, func)
    # Append results
    ig.append(val_ig)
    split_value.append(val)

  if len(ig) == 0:
    return(None,None,None, False)

  else:
    best_ig = max(ig)
    best_ig_index = ig.index(best_ig)
    best_split = split_value[best_ig_index]
    return(best_ig,best_split,numeric_variable, True)

def get_best_split(y, data):
  masks = data.drop(y, axis= 1).apply(max_information_gain_split, y = data[y])
  if sum(masks.loc[3,:]) == 0:
    return(None, None, None, None)
  else:
    masks = masks.loc[:,masks.loc[3,:]]
    split_variable = masks.iloc[0].astype(np.float32).idxmax()
    split_value = masks[split_variable][1] 
    split_ig = masks[split_variable][0]
    split_numeric = masks[split_variable][2]

    return(split_variable, split_value, split_ig, split_numeric)

def make_split(variable, value, data, is_numeric):
  
  if is_numeric:
    data_1 = data[data[variable] < value]
    data_2 = data[(data[variable] < value) == False]
  else:
    data_1 = data[data[variable].isin(value)]
    data_2 = data[(data[variable].isin(value)) == False]
  return(data_1,data_2)

def make_prediction(data, target_factor):
  
  if target_factor:
    pred = data.value_counts().idxmax()
  else:
    pred = data.mean()

  return pred



#Training tree
def train_tree(data,y, target_factor, max_depth = None,min_samples_split = None, min_information_gain = 1e-20, counter=0, max_categories = 20):
  if counter==0:
    types = data.dtypes
    check_columns = types[types == "object"].index
    for column in check_columns:
      var_length = len(data[column].unique()) 
      if var_length > max_categories:
        raise ValueError('The variable ' + column + ' has '+ str(var_length) + ' unique values, which is more than the accepted ones: ' +  str(max_categories))

  if max_depth == None:
    depth_cond = True
  else:
    if counter < max_depth:
      depth_cond = True
    else:
      depth_cond = False

  if min_samples_split == None:
    sample_cond = True
  else:
    if data.shape[0] > min_samples_split:
      sample_cond = True
    else:
      sample_cond = False

  if depth_cond & sample_cond:

    var,val,ig,var_type = get_best_split(y, data)

    if ig is not None and ig >= min_information_gain:
      counter += 1
      left,right = make_split(var, val, data,var_type)
      split_type = "<=" if var_type else "in"
      question =   "{} {}  {}".format(var,split_type,val)
      subtree = {question: []}

      yes_answer = train_tree(left,y, target_factor, max_depth,min_samples_split,min_information_gain, counter)
      no_answer = train_tree(right,y, target_factor, max_depth,min_samples_split,min_information_gain, counter)

      if yes_answer == no_answer:
        subtree = yes_answer
      else:
        subtree[question].append(yes_answer)
        subtree[question].append(no_answer)

    else:
      pred = make_prediction(data[y],target_factor)
      return pred

  else:
    pred = make_prediction(data[y],target_factor)
    return pred

  return subtree



#Random Forest
def draw_bootstrap(data):
    bootstrap_indices = list(np.random.choice(range(len(data)), len(data), replace = True))
    oob_indices = [i for i in range(len(data)) if i not in bootstrap_indices]
    X_bootstrap = data.iloc[bootstrap_indices]
    #y_bootstrap = y_train[bootstrap_indices]
    X_oob = data.iloc[oob_indices].values
    #y_oob = y_train[oob_indices]
    return X_bootstrap, X_oob

def random_feature(data,y):
    feature_ls = list()
    features = data.iloc[:,data.columns != y]
    m = math.isqrt(len(features.columns))
    while len(feature_ls) < m:
        feature_idx = random.sample(range(len(features.columns)),1)
        if feature_idx[0] not in feature_ls:
            feature_ls.extend(feature_idx)
    features = data.iloc[:,feature_ls]
    features.loc[:,y] = data.loc[:,y]
    return features

def random_forest(X_train, y_train, n_estimators, rf, max_depth, min_samples_split,min_information_gain):
    tree_ls = []
    #oob_ls = list()
    for i in range(n_estimators):
        X_bootstrap, X_oob = draw_bootstrap(X_train)
        if rf:
          X_bootstrap = random_feature(X_bootstrap,y_train)
        tree = train_tree(X_bootstrap,y_train,True, max_depth, min_samples_split,min_information_gain)
        tree_ls.append(tree)
        #oob_error = oob_score(tree, X_oob, y_oob)
        #oob_ls.append(oob_error)
    return tree_ls



#Classifier
def classifier(observation, tree):
  question = list(tree.keys())[0] 
  if question.split()[1] == '<=':

    if observation[question.split()[0]] <= float(question.split()[2]):
      answer = tree[question][0]
    else:
      answer = tree[question][1]

  else:

    if observation[question.split()[0]] in (question.split()[2]):
      answer = tree[question][0]
    else:
      answer = tree[question][1]

  if not isinstance(answer, dict):
    return answer
  else:
    residual_tree = answer
    return classifier(observation, answer)
  
def rf_classifier(data,tree,y):
  count=0
  for i in range(0,data.shape[0]): 
    pred = list()
    if len(tree) != 1:
      for j in range(0,len(tree)):
        if type(tree[j]) is dict:
          q = classifier(data.loc[i,data.columns != y],tree[j])
        else:
          q = tree[j]
        pred.extend([q])

        if j == len(tree)-1:
          prediction = most_frequent(pred)
          if prediction == data.loc[i,y]:
            count +=1
    else:  
      if prediction == data.loc[i,y]:
        count +=1

  return count/data.shape[0]
# return prediction
def most_frequent(List):
    counter = 0
    num = List[0]
     
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
    return num


if __name__ == "__main__":
  data = pd.read_csv("data.csv")
  data['obese'] = (data.Index >= 4).astype('int')
  data.drop('Index', axis = 1, inplace = True)
  max_depth = 5
  min_samples_split = 5
  min_information_gain  = 1e-5
  decisiones = train_tree(data,'obese',True, max_depth,min_samples_split,min_information_gain)
  d2 = random_forest(data,'obese', 10, False, 10,min_samples_split,min_information_gain)
  rf_classifier(data,d2,'obese')
  rf_classifier(data,decisiones,'obese')
