import pandas as pd
import numpy as np
import math
import csv
#EN 1993-1-8 [1]
# EN 1993-1-1 
    #For partial safety factors
    #For determining forces and moments applied to joints
#EN 1993-1-9 for joints subject to fatigue
#Linear-elastic or elastic-plastic analysis
#Steel grades: S235, S275, S355, S420, S450, S460

def boltGroup(Ved,n,fub,A,p1,gh,e1,e2,d,d0,fup,tw,tp):
    #Ved is the design force
    #n is number of bolt rows
    #fub is ultimate tensile strength of bolt
    #A is area of the bolt??
    #p1 is pitch between bolts
    #gh is gap 
    #e2 is edge destance
    #d is bolt diameter
    #d0 is bolt hole size
    #fup is ultimate strength of the plate
    #tw is web thickness
    #tp is plate thickness
    z = gh+e2
    B = 6*z/(n*(n+1)*p1)
   
    #bolt shear
    Fvrd = 0.6*fub*A/1.25

    k1p = min(2.8*(e2/d0)-1.7, 2.5)
    a1p = min((e1/(3*d0)),(p1/(3*d0))-0.25, fub/fup,1)
    k2p = min(2.8*(e1/d0)-1.7,1.4*(p1/(3*d0))-1.7,2.5)
    a2p = min(e2/(3*d0),fub/fup,1)

    k1w = min(2.8*(e2/d0)-1.7, 2.5)
    a1w = min(((e1+50)/(3*d0)),(p1/(3*d0))-0.25, fub/fup,1)
    k2w = min(2.8*((e1+50)/d0)-1.7,1.4*(p1/(3*d0))-1.7,2.5)
    a2w = min(e2/(3*d0),fub/fup,1)

    #bearing plate
    Fbverp = k1p*a1p*fub*d*tp/1.25
    Fbhorp = k2p*a2p*fub*d*tp/1.25
    #bearing web
    Fbverw = k1w*a1w*fub*d*tw/1.25
    Fbhorw = k2w*a2w*fub*d*tw/1.25

    Vrd1 = (n*Fvrd/(math.sqrt(1+(B*n)**2)))*10**(-3)
    Vrd2 = (n/( math.sqrt(( (1/Fbverp))**2 + ((B*n/Fbhorp)**2  ))))*10**(-3)
    Vrd3 = (n/( math.sqrt(( (1/Fbverw))**2 + ((B*n/Fbhorw)**2  ))))*10**(-3)

    Vrd = min(Vrd1,Vrd2,Vrd3)
    return Ved <= Vrd

def finPlateShear(Ved,tp,hp,n,d0,e1,e2,fyp,fup):
    #Ved is design force
    #tp is thickness plate
    #hp is height plate
    #n is number of bolt rows
    #d0 is hole diameter
    #e1 is end distance
    #e2 is edge distance
    #fyp is yield strength of plate
    #fup is ultimate strength of plate
    Avnet = tp*(hp-n*d0)
    Ant = tp*(e2-(d0/2))
    Anv = tp*(hp-e1-(n-0.5)*d0)

    Vrdg = (hp*tp/1.27)*(fyp/(math.sqrt(3)))*10**(-3)  
    Vrdn = (Avnet*(fup/(1.1*math.sqrt(3))))*10**(-3)
    Vrdb = (0.5*fup*Ant/1.1 + fyp*Anv/math.sqrt(3))*10**(-3)
    Vrd = min(Vrdg,Vrdn,Vrdb)
    return Ved <= Vrd

def finPlateBending(Ved,hp,tp,z,fyp):
    Wel = tp*hp**2/6
    if hp >= 2.73*z:
        return True
    else:
        Vrd = (Wel*fyp/z)*10**(-3)
    return Ved <= Vrd

def finPlateBuckling(Ved,tp,hp,z,fyp):
    Lambda = 2.8/86.6*(z*hp/(1.5*tp**2))**(0.5)
    lookup_table = {}
    with open("Info//ChiFactor.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            lambda_value = float(row[0])
            corresponding_value = float(row[1])
            lookup_table[lambda_value] = corresponding_value
    x = math.floor(Lambda / 0.05) * 0.05
    lambda2 = round(x, 2)
    Xlt = lookup_table.get(lambda2,None)

    Wel = tp*hp**2/6
    if z > tp/0.15:
        Vrd = min((Wel*Xlt*fyp/(0.6*z))*10**(-3),(Wel*fyp/z)*10**(-3))
    else:
        Vrd = (Wel*fyp/z)*10**(-3)
    return Ved <= Vrd

def supportedShear(Ved,fyb,fub,n,d0,tw,tf,b,rb,hw,A):
    #Ved is design force
    #fyb is yield strength of beam
    #fub is ultimate strength of beam
    #n is number of bolt rows
    #d0 is hole diameter
    #tw is thickness of web
    #tf is thickness of flange
    #b is width of beam
    #rb is root radius of beam
    #hw is straight portion of the web
    #A is section Area of beam
    
    Avnet = Av - n*d0*tw
    Av = max(A - 2*b*tf + (tw + 2*rb)*tf,hw*tw)

    Vrdg = (Av*(fyb/math.sqrt(3)))*10**(-3)
    Vrdn = (Avnet*(fub/(1.1*math.sqrt(3))))*10**(-3)
    

    Vrd = min(Vrdg,Vrdn)
    return Ved <= Vrd

def supportedBending(Ved,p1,hb,tw,n,e2,fyb,z):
    #Ved is design force
    #p1 is bolt pitch
    #hb is height of web
    #tw is thickness of web
    #n is number of bolt rows
    #e2 is end distance
    #fyb is yield strength of beam
    #z is distance between supporting web and bolt
    Vbc = Ved*(n-1)*p1/hb
    Vpl1 = tw*e2*fyb/math.sqrt(3)
    Vpl2 = tw*(n-1)*p1*fyb/math.sqrt(3)
    if Vbc <= 0.5*Vpl2:
        Mc = (fyb*tw/6)*((n-1)*p1)**2
    else:
        Mc = ((fyb*tw/6)*((n-1)*p1)**2)*(1-(2*Vbc/Vpl2-1)**2)
    Vrd = (Mc + Vpl1*(n-1)*p1)*10**(-3)
    return Ved*z <= Vrd

def supportingShear(Ved,hp,tp,fy):
    Av = hp*tp
    Frd = (Av*(fy/math.sqrt(3)))*10**(-3)
    return Ved/2 <= Frd


    #punching shear
def supportingPunching(Ved,fu,tp,hp,z):
    #Ved is design force
    #fu is ultimae strength supporting member
    #tp is thickness of plate
    #hp is height of plate
    return tp <= fu*tp*hp**2/(Ved*6*z*1.25)

def finPlateTying(Fed,tp,hp,n,p1,d0,e2,fup,fyp):
    #Fed is tying force
    #tp is thickness plate
    #hp is height of plate
    #n is number of bolt rows
    #p1 is bolt pitch
    #d0 is hole diameter
    #e2 is edge distance
    #fup is ultimate strength of plate
    #fyp is yield strength of plate
    Ant = tp*((n-1)*p1-(n-1)*d0)
    Anv = 2*tp*(e2-d0/2)
    Anet = tp*(hp-d0*n)

    Frdb = (fup*Ant/1.1 + fyp*Anv/math.sqrt(3))*10**(-3)
    Frdn = (0.9*Anet*fup/1.1)*10**(-3)
    Frd = min(Frdb,Frdn)
    return Fed <= Frd

def supportedTying(Fed,tw,p1,d0,e2,fub,fyb,n,hb):
    #Fed is tying force
    #tw is thickness of web
    #hp is height of plate
    #n is number of bolt rows
    #p1 is bolt pitch
    #d0 is hole diameter
    #e2 is edge distance
    #fup is ultimate strength of plate
    #fyp is yield strength of plate
    Ant = tw*((n-1)*p1-(n-1)*d0)
    Anv = 2*tw*(e2-d0/2)
    Anet = tw*(hb-d0*n)

    Frdb = (fub*Ant/1.1 + fyb*Anv/math.sqrt(3))*10**(-3)
    Frdn = (0.9*Anet*fub/1.1)*10**(-3)
    Frd = min(Frdb,Frdn)
    return Fed <= Frd

def supportingTying(Fed,fub,tb,tp,hp,dc,s):
    #Fed is tying force
    #fub is ultimate strength of column
    #tb is thickness of column web
    #tp is thickness of plate
    #hp is heigth of plate
    #dc is depth of straight portion of the column web
    #s is leg length of fillet weld
    n = hp/dc
    B = (tp+2*s)/dc
    Mpl= 0.25*fub*tb
    Frd = ((8*Mpl/(1.1*(1-B)))*(n+1.5*(1-B)**0.5))*10**(-3)
    return Fed <= Frd