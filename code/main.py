import numpy as np
import pandas as pd
import model.decisiontree as decisiontree
import model.RFEMimport as RFEMimport
import detailing.design as design
from joblib import dump, load
from sklearn.model_selection import train_test_split
import validation.crossValidation as crossValidation

#########################################################################
#bim import
#########################################################################

#Test model
#Members = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\RFEM Export\\Test\\Members.csv",sep = ';',header = None, names = ["Member No", "Line No", "Member Type","Section Distribution","Rotation","Section Start i","Section end j","Section internal k","Hinge Start i","Hinge end J","Eccentricity Start i","Eccentricity End j","Length","Volume","Mass","Position","Options","Comment"])
#Lines = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\RFEM Export\\Test\\Lines.csv",sep = ';', header = None, names = ["Line No","Nodes","Line Type","Length","Position","Options","Comment"])
#Nodes = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\RFEM Export\\Test\\Nodes.csv",sep = ';',header = None, names = ["Node No","Node Type","Reference Node","Coordinate System","Coordinate Type","X","Y","Z","Global X","Global Y","Global Z","Optins","Comment"])
#Forces = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\RFEM Export\\Test\\CO2 ! Members ! Internal Forces.csv",sep =';',header = None, names = ["Member No","Node No","Location","NaN","N","Vy","Vz","Mt","My","Mz","Section"])
#Material = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\RFEM Export\\Test\\Materials.csv",sep = ';',header = None, names = ["Material No","Material Name","Material Type","Material Model","Elasticity Modulus","Shear Modulus","Poisson's Ratio","Specific Weight","Mass Density","Coefficient of thermal expansion","Options","Comment"])
#Section = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\RFEM Export\\Test\\Sections.csv",sep = ';',header = None, names = ["Section No","Section Name","Assigned","Material","Axial A","Shear Ay","Shear Az","Torsion J","Bending Iy","Bending Iz","Principal Axes","Width b","Depth h","Options","Section"])

#Real model
#Members = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\Data\\RFEMDATAEXPORT\\Rekenmodel - rev B\\Members.csv",sep = ';',header = None, names = ["Member No", "Line No", "Member Type","Section Distribution","Rotation","Section Start i","Section end j","Section internal k","Hinge Start i","Hinge end J","Eccentricity Start i","Eccentricity End j","Length","Volume","Mass","Position","Options","Comment"])
#Lines = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\Data\\RFEMDATAEXPORT\\Rekenmodel - rev B\\Lines.csv",sep = ';',header = None, names = ["Line No","Nodes","Line Type","Length","Position","Options","Comment"])
#Nodes = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\Data\\RFEMDATAEXPORT\\Rekenmodel - rev B\\Nodes.csv",sep = ';',header = None, names = ["Node No","Node Type","Reference Node","Coordinate System","Coordinate Type","X","Y","Z","Global X","Global Y","Global Z","Optins","Comment"])
#Forces = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\Data\\RFEMDATAEXPORT\\Rekenmodel - rev B\\CO1 ! Members ! Internal Forces.csv",sep = ';',header = None, names = ["Member No","Node No","Location","NaN","N","Vy","Vz","Mt","My","Mz","Section"])
#Material = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\Data\\RFEMDATAEXPORT\\Rekenmodel - rev B\\Materials.csv",sep = ';',header = None, names = ["Material No","Material Name","Material Type","Material Model","Elasticity Modulus","Shear Modulus","Poisson's Ratio","Specific Weight","Mass Density","Coefficient of thermal expansion","Options","Comment"])
#Section = pd.read_csv("C:\\Users\\g.oudevrielink\Documents\\Data\\RFEMDATAEXPORT\\Rekenmodel - rev B\\Sections.csv",sep = ';',header = None, names = ["Section No","Section Name","Assigned","Material","Axial A","Shear Ay","Shear Az","Torsion J","Bending Iy","Bending Iz","Principal Axes","Width b","Depth h","Options","Section"])
#classes = pd.read_csv("C:\\Users\\g.oudevrielink\\Documents\\Data\\classes_stripped.csv")
#classes = classes['connection type']
#########################################################################
#Data
#########################################################################
#input = RFEMimport.inputData(Members,Lines,Nodes,Section,Forces)
#data,dataInfo = RFEMimport.rfInput(input,classes)
#data,dataInfo = data[data['Output'] != 0],dataInfo[data['Output'] != 0]
#data,dataInfo = data.reset_index(drop=True),dataInfo.reset_index(drop=True)

#data.to_csv('data_Stripped.csv',index=False)
#dataInfo.to_csv('data_Info.csv',index=False)
#print(data,dataInfo)
#########################################################################
#Data splitting
data = pd.read_csv("Info\\dataTrain\\data_Stripped.csv")

#y = data['Output']

#X_train, X_test, y_train, y_test = train_test_split(data,y, test_size = 0.3, random_state = 42)



#########################################################################
#Plot joints
#########################################################################

#RFEMimport.plotJoint(Members,Lines,Nodes,Section,Forces)


#########################################################################
#Training model on RFEM set random output data
#########################################################################'

#max_depth = 5
#min_samples_split = 5
#min_information_gain  = 1e-5
#d2 = decisiontree.train_tree(data,'Output',True, max_depth,min_samples_split,min_information_gain)
#d2 = decisiontree.random_forest(data,'Output', 100 , True, max_depth, min_samples_split,min_information_gain)
#print(d2)
#dump(d2,'rfmodeel.joblib')


#########################################################################
#Prediction
#########################################################################
#data = pd.read_csv("Info\\dataTrain\\data_Stripped.csv")
#dataInfo = pd.read_csv("Info\\dataTrain\\data_Info.csv")

#d2 = load('rfmodeel.joblib')
#decisiontree.rf_classifier(data,d2,'Output')




#get mock data
#run the model
#run detailing based on prediction
#output class

#test = data.iloc[202:203].reset_index(drop=True)
#test2 = dataInfo.iloc[202:203].reset_index(drop=True)


def connection(joint,jointinfo,d2):
    prediction = decisiontree.rf_classifier(joint,d2,'Output')
    joint = joint.loc[0]
    jointinfo = jointinfo.loc[0]
    if prediction == 1:
        connection = design.PDEP(joint,jointinfo)
    elif prediction == 2:
        connection = design.FinPlate(joint,jointinfo)
    elif prediction == 3:
        connection = design.GussetPlate(joint,jointinfo)
    return connection

k = crossValidation.kFoldValidation(data,10,20,5)
print(k)