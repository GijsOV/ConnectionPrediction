import pandas as pd
import numpy as np
import math
#EN 1993-1-8
# EN 1993-1-1 
    #For partial safety factors
    #For determining forces and moments applied to joints
#EN 1993-1-9 for joints subject to fatigue
#Linear-elastic or elastic-plastic analysis
#Steel grades: S235, S275, S355, S420, S450, S460

#standardised design



#Design checks FDEP
def webShear(Ved,h,tf,tw,rb,Ab,b,fyb):
    #Ved is design force
    #h is height of supported beam
    #tf is thickness of supported beam flange
    #tw is the thickness of the supported beam web
    #rb is the root radius of the supported beam
    #Ab is the gross area of the supported beam
    #b is the width of the supported beam
    #fyb is yield strenght of supporte dbeam
    hw = h-2*tf
    Av = min(Ab-2*b*tf + tf*(tw + 2*rb),hw*tf)
    Vc = Av*(fyb/(math.sqrt(3)))*10**(-3)

    if Ved <= Vc:
        return True
    else:
        return False
    

def boltGroup(Ved,av,fub,A,e2,d0,p1,fup,d,tp,n):
    #Ved is design 
    #av = 0.6 for 8.8 bolts
    #fub is ultimate tensile strength of bolt
    #fup is ultimate tensile strength of plate
    #A is tensile stress area of bolt
    #e2 is edge distance
    #d0 is hole size (22 for M20 bolts)
    #p1 is vertical pitch
    #d is bolt diameter
    #tp is thickness of plate
    #n is number of bolts

    #Shear resistance of single bolt
    Fv = av*fub*A/1.25

    #bearing resistance of single bolt
    k1 = min(2.8*(e2/d0)-1.7,2.5)
    ab = min((p1/(3*d0))-0.25,fub/fup,1)
    Fbp = (k1*ab*fup*d*tp/1.25)*10**(-3)

    if Fbp <= 0.8*Fv:
        Frd = n*Fbp
    else:
        Frd = 0.8*n*Fv

    if Ved <= Frd:
        return True
    else:
        return False
    
    
def supportingBeamColumnShearBearing(Ved,t2,d,p1,p3,n1,d0,fy,fu):
    #Ved is design force
    #t is thickness of supporting element
    #d is diameter of the bolt
    #p1 is vertical pitch between bolts
    #p3 is horizontal pitch between bolts
    #n1 is number of bolt 
    #d0 diameter of bolt holes
    #fy yiel strength of support element
    #fu is ultimate strength of support element.


    et = 5*d
    eb = min((p3/2),)
    Av = (et + (n1-1)*p1 + eb)*t2
    Avnet = Av -n1*d0*t2
    Vrd = min( (Av*fy/math.sqrt(3))*10**(-3), (Avnet*fu/(math.sqrt(3)*1.25))*10**(-3))

    if Ved/2 <= Vrd:
        return True
    else:
        return False
    
    
def plateBoltsTying(Fed,p1,p3,e2,tw,n1,dw,tp,fup,N,fub,As,a):
    #Fed is the design force
    #p1 is the vertical pitch
    #p3 is the gauge
    #e2 is edge distance
    #tw is web thickness of supported beam
    #n1 is the number of bolt rows
    #dw is the diameter of the washer or the sidth across points of the bolt or nut as relevant
    #tp is the thickness of plate
    #fup is the ultimate strength of the plate
    #N is the number of bolts
    #fub ultimate strength of the bolt
    #As is the tensile stress area of the bolt
    #a is the weld throat thickness

    ew = dw/4
    Ft = 0.9*fub*As/1.1
    m = (p3-tw-(1.6*a*math.sqrt(2)))/2
    n = min(e2,1.25*m)

    lt = max(5.25*m-(4*m +1.25*e2)/2,(4*m +1.25*e2)/2)
    leff = 2*lt + p1*(n1-1)
    Mpl = 0.25*leff*(tp**2)*fup/1.1

    #Mode 1 (complete yielding of the end plate)
    Frd1 = ((8*n-2*ew)*Mpl)/(2*m*n-(ew*(m+n)))*10**(-3)

    #Mode 2 (bolt failure with yielding of the end plate)
    Frd2 = (2*Mpl+n*(N*Ft))/(m+n)*10**(-3)

    #Mode 3
    Frd3 = N*Ft*10**(-3)

    Frd = min(Frd1,Frd2,Frd3)
    return Fed <= Frd


def supportedWebTying(Fed,hp,fub,tw,tf):
    #hp is height of plate
    #fub is ultimate strength beam
    #tw is web thickness of supported beam
    #tf is flange thickness of supported beam
    Frd = ((tw*(hp-2*tf)*fub)/1.1)*10**(-3)
    return Fed <= Frd

def supportingColumnWeb(Fed,n1,p1,d0,p3,d2,fu,tw):
    #n1 is the number of bolt rows
    #p1 vertical pitch
    #d0 diameter of bolt hole
    #p3 horizontal pitch
    #d2 depth of straight portion of web
    #fu ultimate strength of supporting element
    #tw thickness of column web

    N1 = ((n1-1)*p1-(0.5*n1)*d0)/d2
    B1 = p3/d2
    Y1 = d0/d2
    Mpl = (fu*tw**2)/(4.4)
    Frd = (8*Mpl)/(1-B1)*(N1+1.5*(1-B1)**0.5*(1-Y1)**0.5)*10**(-3)
    return Fed <= Frd
