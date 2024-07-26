import pandas as pd
import math
from connectionDetaling import PDEP_INT, FDEP_INT, FinPlate_INT, GussetPlate_INT
import sys
sys.path.append('C:/Users/g.oudevrielink/Documents/Project/connection-prediction/code')
sys.path.append('C:/Users/g.oudevrielink/Documents/Project/connection-prediction/Info')
import designchecks.dcPDEP as PDEP
import designchecks.dcFDEP as FDEP
import designchecks.dcFP as FP
import designchecks.dcGP as GP
data = pd.read_csv("dataTrain\\data_Stripped.csv")
dataInfo = pd.read_csv("\dataTrain\\data_Info.csv")
materialInfo = pd.read_csv("typeInfo\\materialInfo.csv")
sectionInfo = pd.read_csv("typeInfo\\IsectionInfo.csv")

def nbolts(hb):
#n1 is number of bolts in vertical row 
    if hb < 305.1: 
        n1 = 2 
    elif hb < 406:
        n1 = 3
    elif hb < 449.8:
        n1 = 4
    elif hb < 560.3:
        n1 = 5
    elif hb < 602.6:
        n1 = 6
    elif hb < 683.5:
            n1 = 7
    elif hb < 762.2:
        n1 = 8
    elif hb < 834.9:
            n1 = 9
    elif hb < 921:
        n1 = 10
    else:
        n1 = 11
    return n1

def materialStrength(mat):
    #material needs to be transfered to another name, from string to integer, this will result in this function not working
    #Try to import materInfo.csv, easier to add additional materials
    if mat == '2 - S235 | Isotropic | Linear El':
        fy = 235
        fu = 360

    if mat == '4 - S275 | Isotropic | Linear El':
        fy = 275
        fu = 410

    if mat == '3 - S355 | Isotropic | Linear El':
        fy = 355
        fu = 470

    return fy,fu

def boltStrength(grade):
    a = grade // 10
    b = grade % 10
    fyf = a*b*10
    fuf = a*100
    return fyf,fuf

def boltSize(size):
    d = size
    if d <= 24:
        d0 = d + 2
    else:
        d0 = d+3
    av = 0.6
    if d == 16:
        A = 157
        dw = 26
    elif d == 18:
        A = 192
        dw = 33
    elif d == 20:
        A = 245
        dw = 40
    return d,d0,av,A,dw

def PDEP(joint,jointInfo):
    sectionInfo.set_index(sectionInfo.columns[0], inplace=True)
    #Section of supported member
    section1 = sectionInfo.loc[jointInfo['supportedSection']]
    #Section of supporting member
    section2 = sectionInfo.loc[jointInfo['supportingSection']]


    #Standardized properties based on supported member size
    n1 = nbolts(section1.loc['h'])
    e1,e2,p1 = 40,30,70
    hp = (n1-1)*p1+2*e1

    if section1.loc['h'] >= 524.7:
        bp = 200
        tp = 12
        p3 = 140
    else:
        bp = 150
        tp = 10
        p3 = 90


    #Running design checks
    #defining parameters for calculation, b refers to beams - f refers to fasteners
    #p refers to plates
    Ved = joint['Ved']
    Fed = joint['Fed']
    fyp,fup = materialStrength("4 - S275 | Isotropic | Linear El")
    fyf,fuf = boltStrength(88)
    d,d0,av,A,dw = boltSize(20)
    n = n1*2
    a = 4.24
 
    #some element properties for calculations
    fyb1,fub1 = materialStrength(jointInfo['supportedMaterial'])
    fyb2,fub2 = materialStrength(jointInfo['supportingMaterial'])
    ds1,ds2 = section1.loc['d'],section2.loc['d']
    tw1,tw2 = section1.loc['tw1'],section2.loc['tw']
    tf1,tf2 = section1.loc['tf1'],section2.loc['tf']
    r1,r2 = section1.loc['r1'],section2.loc['r1']
    A1,A2 = section1.loc['A1'],section2.loc['A1']
    b1,b2 = section1.loc['b'],section2.loc['b']
    ds1,ds2 = section1.loc['d'],section2.loc['d']
    
    #Check 1 web shear
    while PDEP.webShear(Ved,hp,tw1,fyb1) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1+2*e1
        n = n1*2
        print("1")

    #Check 2 bolt group
    while PDEP.boltGroup(Ved,e1,e2,p1,p3,d,d0,n,av,A,tp,fub1,fup) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1+2*e1
        n = n1*2
        print("2")
    #check 3 endplate shear
    while PDEP.endPlateShear(Ved,hp,tp,tw1,fyp,n1,d0,fup,p3,e1,e2) != True:
        if tp == 10:
            tp = 12
        else:
            n1 = n1 + 1
            hp = (n1-1)*p1+2*e1
            n = n1*2
        print("3")
    #CHECK 4 Supporting beam shear and bending
    while PDEP.supportingBeamColumnShearBendingSingle(Ved,tw2,e1,e1,n1,p1,p3,d,d0,fyb2,fub2) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1+2*e1
        n = n1*2
        print("4")
       
    #Checks in case supported beam is notched.
    notch = False
    if notch == True:
        PDEP.singleNotchResistance()
        PDEP.SingleNotchStability()
        PDEP.DoubleNotchStability()

    #tying checks.
        
    #CHECK 8 plateBoltsTying
    while PDEP.plateBoltsTying(Fed,fub1,A,dw,n,p3,d0,e1,e2,tw1,a,p1,tp,n1,fup) != True:
        if tp == 10:
            tp = 12
        else:
            n1 = n1 + 1
            hp = (n1-1)*p1+2*e1
            n = n1*2
        print("8")
    #CHECK 9 supported web tying
    while PDEP.supportedWebTying(Fed,hp,fub,tw2) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1+2*e1
        n = n1*2
        print("9")
    #CHECK 10 supporting column web tying
    while PDEP.supportingColumnWeb(Fed,n1,p1,d0,p3,ds2,fub2,tw2) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1+2*e1
        n = n1*2
        print("10")

    connection = PDEP_INT("4 - S275 | Isotropic | Linear El",hp,bp,tp,n1,p3,20,88)
    return connection

def FDEP(joint,jointInfo):
    sectionInfo.set_index(sectionInfo.columns[0], inplace=True)
    #Section of supported member
    section1 = sectionInfo.loc[jointInfo['supportedSection'][0]]
    #Section of supporting member
    section2 = sectionInfo.loc[jointInfo['supportingSection'][0]]


    #Standardized properties based on supported member size
    n1 = nbolts(section1.loc['h'])
    p1 = 70
    a,al = 4.24, 6
    hp = section1.loc['h'] + 2*al
    e1 = (hp - (n1-1)*p1)/2
    e2 = 30

    if section1.loc['h'] >= 524.7:
        bp = 200
        tp = 12
        p3 = 140
    else:
        bp = 150
        tp = 10
        p3 = 90
    

    #Running design checks
    #defining parameters for calculation, b refers to beams - f refers to fasteners
    #p refers to plates
    Ved = joint['Ved']
    Fed = joint['Fed']
    fyp,fup = materialStrength(connection.material)
    fyf,fuf = boltStrength(connection.boltGrade)
    d,d0,av,A,dw = boltSize(connection.boltSize)
    n = n1*2
    a = 4.24

    #some element properties for calculations
    fyb1,fub1 = materialStrength(jointInfo['supportedMaterial'])
    fyb2,fub2 = materialStrength(jointInfo['supportingMaterial']) 
    tw1,tw2 = section1.loc['tw'],section2.loc['tw']
    tf1,tf2 = section1.loc['tf'],section2.loc['tf']
    r1,r2 = section1.loc['r1'],section2.loc['r1']
    A1,A2 = section1.loc['A1'],section2.loc['A1']
    b1,b2 = section1.loc['b'],section2.loc['b']
    ds1,ds2 = section1.loc['d'],section2.loc['d']

    #CHECK 1 web shear
    if FDEP.webShear(Ved,hp,tf1,tw1,r1,A1,b1,fyb1) != True:
        print("1 Reinforcement of the web is needed")

    #CHECK 2 bolt group
    while FDEP.boltGroup(Ved,av,fuf,A,e2,d0,p1,fup,d,tp,n) != True:
        n1 = n1 + 1
        n = n1*2  
        e1 = (hp - (n1-1)*p1)/2
        print("2")

    #CHECK 3 supporting beam shear and bearing
    while FDEP.supportingBeamColumnShearBearing(Ved,tw2,d,p1,p3,n1,d0,fyb2,fub2) != True:
        n1 = n1 + 1
        n = n1*2
        e1 = (hp - (n1-1)*p1)/2
        print("3")

    #CHECK 4 plate bolts tying
    while FDEP.plateBoltsTying(Fed,p1,p3,e2,tw1,n1,dw,tp,fup,n,fuf,A,a) != True:
        if tp == 10:
            tp = 12
        else:
            n1 = n1 + 1
            n = n1*2 
            e1 = (hp - (n1-1)*p1)/2
        print("4")
    
    #CHECK 5 supported web tying
    if FDEP.supportedWebTying(Fed,hp,fub1,tw1,tf1) != True:
        print("5 Reinforcmeent of the web is needed")

    #CHECK 6 
    while FDEP.suportingColumnWeb(Fed,n1,p1,d0,p3,ds2,fub2,tw2) != True:
        n1 = n1 + 1
        n = n1*2
        e1 = (hp - (n1-1)*p1)/2
        print("6")

    connection = FDEP_INT("4 - S275 | Isotropic | Linear El",hp,bp,tp,n1,p3,20,88)
    return connection

def FinPlate(joint,jointInfo):
    sectionInfo.set_index(sectionInfo.columns[0], inplace=True)
    #Section of supported member
    section1 = sectionInfo.loc[jointInfo['supportedSection'][0]]
    #Section of supporting member
    section2 = sectionInfo.loc[jointInfo['supportingSection'][0]]


    #Standardized properties based on supported member size
    n1 = nbolts(section1.loc['h'])
    e1,tp,p1 = 40,10,70
    hp = (n1-1)*p1 + 2*e1

    if section1.loc['h'] > 610:
        bp = 120
        gh = 20
        e2 = 60
    else:
        bp = 100
        gh = 10
        e2 = 50
 

    #Running design checks
    #defining parameters for calculation, b refers to beams - f refers to fasteners
    #p refers to plates
    Ved = joint['Ved']
    Fed = joint['Fed']
    fyb1,fub1 = materialStrength(jointInfo['supportedMaterial'])
    fyb2,fub2 = materialStrength(jointInfo['supportingMaterial'])
    fyp,fup = materialStrength("4 - S275 | Isotropic | Linear El")
    fyf,fuf = boltStrength(88)
    d,d0,av,A,dw = boltSize(20)
    n = n1
    z = gh+e2
    a,al = 5.66, 8

    #some element properties for calculations
    fyb1,fub1 = materialStrength(jointInfo['supportedMaterial'])
    fyb2,fub2 = materialStrength(jointInfo['supportingMaterial'])
    ds1,ds2 = section1.loc['d'],section2.loc['d']
    tw1,tw2 = section1.loc['tw1'],section2.loc['tw']
    tf1,tf2 = section1.loc['tf1'],section2.loc['tf']
    r1,r2 = section1.loc['r1'],section2.loc['r1']
    A1,A2 = section1.loc['A1'],section2.loc['A1']
    b1,b2 = section1.loc['b'],section2.loc['b']
    ds1,ds2 = section1.loc['d'],section2.loc['d']

    #CHECK 1 
    while FP.boltGroup(Ved,n1,fuf,A,p1,gh,e1,e2,d,d0,fup,tw1,tp) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1 + 2*e1
        print("1")

    #CHECK 2
    while FP.finPlateShear(Ved,tp,hp,n1,d0,e1,e2,fyp,fup) != True:
        if tp == 10:
            tp = 12
        else:
            n1 = n1 + 1 
            hp = (n1-1)*p1 + 2*e1
        print("2")

    #CHECK 3
    while FP.finPlateBending(Ved,hp,tp,z,fyp) != True:
        if tp == 10:
            tp = 12
        else:
            n1 = n1 + 1 
            hp = (n1-1)*p1 + 2*e1  
        print("3")

    #CHECK 4
    while FP.finPlateBuckling(Ved,tp,hp,z,fyp) != True:
        tp = tp + 2
        print("4")

    #CHECK 5
    while FP.supportedShear(Ved,fyb1,fub1,n1,d0,tw1,tf1,b1,r1,ds1,A) != True:
        if tp == 10:
            tp = 12
        else:
            n1 = n1 + 1 
            hp = (n1-1)*p1 + 2*e1  
        print("5")

    #CHECK 6
    if FP.supportedBending() != True:
        print("6 reinforcement of the web is needed")

    #CHECK 7
    while FP.supportingShear(Ved,hp,tp,fyb2) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1 + 2*e1
        print("7")

    #CHECK 8
    while FP.supportingPunching(Ved,fub2,tp,hp,z) != True:
        n1 = n1 + 1
        hp = (n1-1)*p1 + 2*e1
        print("8")

    #CHECK 9
    while FP.finPlateTying(Fed,tp,hp,n1,p1,d0,e2,fup,fyp) != True:
        tp = tp + 2
        print("9")

    #CHECK 10
    while FP.supportingTying() != True:
        n1 = n1 + 1
        hp = (n1-1)*p1 + 2*e1
        print("10")

    connection = FinPlate_INT("4 - S275 | Isotropic | Linear El",hp,bp,tp,n1,p1,gh,20,88)
    return connection


def GussetPlate(joint,jointInfo):
    g, tp, tt, n1, e1, e2, p1, p3 = 500, 10, 10, 2, 40, 30, 70, 90
    if joint.shape[0] == 2:
        section1 = sectionInfo[sectionInfo['Section'] == jointInfo.iloc[0]['supportingSection']]
        section2 = sectionInfo[sectionInfo['Section'] == jointInfo.iloc[1]['supportingSection']]
        angle1 = round(joint.iloc[0]['Angle'])
        angle2 = round(joint.iloc[1]['Angle'])
        angle = min(angle1,angle2)
        hc = 0.5*section1.iloc[0]['A']
        hb = 0.5*section2.iloc[0]['A']
        wp = float(abs(g*math.cos(angle)-hc))
        hp = float(abs(g*math.sin(angle)-hb))

    else:
        section = sectionInfo[sectionInfo['Section'] == jointInfo['supportingSection']]
        angle = round(joint['Angle'])
        hb = 0.5*section.iloc[0]['A']
        wp = float(abs(g*math.cos(angle)))
        hp = float(abs(g*math.sin(angle)-hb))


    #Running design checks
    #defining parameters for calculation, b refers to beams - f refers to fasteners
    #p refers to plates
    Ved = joint['Ved']
    fyp,fup = materialStrength("4 - S275 | Isotropic | Linear El")
    fyt,fut = materialStrength("4 - S275 | Isotropic | Linear El") 
    E = 210000
    fyf,fuf = boltStrength(88)
    d,d0,av,A,dw = boltSize(20)
    a = 4.24
    n2 = 1
    Wt = 2*e2 + p3*(n2-1)
    n = n1 * n2

    #CHECK 1
    while GP.gussetPlateBoltGroup(Ved,e1,e2,p1,d,d0,n,A,tp,fuf,fup) != True:
        if tp == 10:
            tp = 12
        else:
            n1 = n1 + 1 
        print("1")

    #CHECK 2
    while GP.gussetPlateShear(Ved,tp,n2,d0,e2,p3,fup,fyp) != True:
        tp = tp + 2
        print("2")

    #CHECK 3
    while GP.gussetPlateAxial(Ved,Wt,tt,tp,e1,p1,n1,E,angle,fyp,fyt,hb,hc) != True:
        tp = tp + 2
        print("3")

    connection = GussetPlate_INT('S275',hp,wp,tp,n1,p1,angle,g,20,88)
    return connection


