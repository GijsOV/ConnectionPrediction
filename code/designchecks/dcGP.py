import pandas as pd
import numpy as np
import math
#EN 1993-1-8 [1]
# EN 1993-1-1 
    #For partial safety factors
    #For determining forces and moments applied to joints
#EN 1993-1-9 for joints subject to fatigue
#Linear-elastic or elastic-plastic analysis
#Steel grades: S235, S275, S355, S420, S450, S460

def gussetPlateBoltGroup(Ved,e1,e2,p1,p3,d,d0,n,A,tp,fub,fup):
    #Ved is design force
    #e1 is end distance
    #e2 is edge distance
    #p1 is bolt pitch
    #p3 is bolt gauge
    #d is bolt diameter
    #d0 is bolt hole diameter
    #n is number of bolts
    #A is tensile stress area of the bolt
    #tp is the thickness of the plate
    #fub is ultimate tensile strength of the bolt
    #fup is the ultimate tensile strength of the plate
    av = 0.6
    Fv = (av*fub*A)/1.25

    abp = min(e1/(3*d0),p1/(3*d0)-0.25,fub/fup,1)
    k1p = min(2.8*e2/d0-1.7,1.4*p3/d0-1.7,2.5)
    Fbp = ((k1p*abp*fup*d*tp)/1.25)*10**(-3)
    if Fbp <= 0.8*Fv:
        Frd = n*Fbp
    else:
        Frd = 0.8*n*Fv
    return Ved <= Frd

def gussetPlateShear(Ved,tp,n2,d0,e2,p3,fu,fy):
    #Ved is design forve
    #tp is thickness of the plate
    #n2 is number of bolt lines
    #d0 is diameter of bolt hole
    #e2 is edge distance
    #p3 is bolt gauge
    #fu is the ultimate strength of the plate
    #fy is the yield strength of the plate
    Anet = tp*(2*e2+(n2-1)*p3-n2*d0)

    Vrdg = tp*2*e2*fy*10**(-3)
    Vrdn = (0.9*Anet*fu/1.1)*10**(-3)
    Vrd = min(Vrdg,Vrdn)
    return Ved <= Vrd

def gussetPlateAxial(Ved,Wt,tt,tg,e1,p1,n1,E,angle,fyt,fyg,hb,hc):
    #Ved is design force
    #Wt is width of tab plate
    #tt is thickness of tab plate
    #tg is thicknss of gusset plate
    #e1 is end distance
    #p1 is bolt pitch
    #n1 is number of bolt rows
    #E is the elasticity modulus of plate steel
    #fyt is yield strength of the tab plate
    #fyg is yield strength of the gusset plate
    #hb is half of the beam depth
    #hc is half of the column depth
    Lt = e1
    Lg = 0
    Ll = p1*(n1-1)
    Wg = math.sqrt((hc-250*math.cos(math.radians(angle)))**2+(500*math.sin(math.radians(angle))-250*math.sin(math.radians(angle)))**2) + math.sqrt((250*math.cos(math.radians(angle))-500*math.cos(math.radians(angle)))**2+(250*math.sin(math.radians(angle))-hb)**2)

    It = Wt*tt**3/12
    Il = 0.5*(Wt+Wg)*(tt+tg)**3/12
    Ig = Wg*tg**3/12

    Mt = 1/((Lt/(E*It)) +  (Ll/(2*E*Il)))
    Mg = 1/((Lg/(E*Ig)) + (Ll/(2*E*Il)))

    ut = Mt/(Mt+Mg)
    ug = Mg/(Mt+Mg)

    Nrdtab = (Wt*fyt*tt**2/(2.5*1.05*(tt+tg)*ut+tt))*10**(-3)
    Nrdguss = (Wg*fyg*tg**2/(2.5*1.05*(tt+tg)*ug+tg))*10**(-3)
    Nrd = min(Nrdtab,Nrdguss)
    return Ved <= Nrd