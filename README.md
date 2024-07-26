# Voortman Connection-Prediction using machine learning

## Personal note: to push to github 
### open git bash
### cd "directory", can also open trough file explorer
### git status
### git add .
### git commit -m "message"
### git push origin main


## Description
### This project aims at predicting connection designs in steel constructions by using machine learning. Datasets of BIM models are used to train a Decision tree model.

### Model is build in Python

## Usage
### The main file is used to run the model. Following commands are used:

### RFEMimport.inputData(Members, Lines, Nodes, Section, Forces): Fucntion used to convert csv files originating from RFEM to an input array. Input arguments are files exported from RFEM. Important is that the RFEM is exported in csv format using the available cls export. Using the RFEM table exporter -> settings: Application/File format = CSV, Options = Export table header, List separator = Semicolon ';'. use pd.readcsv to import: Members.csv, Lines.csv, Nodes.csv, Materials.csv, Sections.csv, Forces.csv. note: Forces refers to the loadcombination calculated for the specific model. 

### RFEM.rfInput(input,output): Function used to combine the input and output for training ml models. Input results from RFEMimport.inputData(). For classifying new observation, output can be a zero column.

### decisiontree.train_tree(data, y, target_factor, max_depth,min_samples_split, min_information_gain, counter=0, max_categories): Function to train decision tree. data: input array resulting from RFEM.rfInput. y: column name of the output called 'Output'. target_factor: True for classification, False for regression. max_depth: heuristic for max depth of the tree. min_samples_split: heuristic for minimal samples to be split. min_information_gain: heuristic for minimal information gain needed to make the split, max_categories: heuristic to check for maximal amount of features allowed to train.

### def random_forest(data, y, n_estimators, rf, max_depth, min_samples_split,min_information_gain): Function to train a random forest model. Inputs similar to decisiontree.train_tree. n_estimators: number of estimator trees. rf: True for enabling random feature selection, False for disabling random feature selection.

### decisiontree.rf_classifier(data,tree,y): Function to classify a new observation. data: observation resulting from RFEM.rfInput. tree: name of the used tree. y: column name of the ouput called 'Output'. note to self: classifier currently validates and is made for using training data.
