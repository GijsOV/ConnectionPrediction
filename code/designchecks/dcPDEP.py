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




#Design checks PDEP
def webShear(Ved,hp,tw,fyb):
    #Ved is design force
    #hp is depth of plate
    #tw is thickness of supported web
    #fyb is yield strength of supported beam
    Vc = (0.9*tw*hp*fyb/(math.sqrt(3)))*10**(-3)
    if Vc >= Ved:
        return True
    else:
        return False
    

def singleNotchResistance(Ved,fy,ln,lh,tp,h,tf,tw,b,rb): \
    #Ved is design force
    #fy yield strength of supported beam
    # ln is notch width
    #lh is notch height
    #tp is thickness of plate
    #h is depth of supported beam
    #tf is thickness of flange
    #tw is thickness of web
    #b is width of the beam
    #rb is root fillet radius of the supported beam

    A = (h-lh-tf)*tw+tf*b
    Av = A-b*tf+(tw + 2*rb)*(tf/2)
    Vpl = (Av*fy/math.sqrt(3))*10**(-3)
    hw = (h-lh)-tf
    b1 = b-tw
    Ax = b*tf + hw*tw
  
    yc = (1/(2*A))*(tw*(h-lh)**2+b1*tf**2)
    Ix0 = ((tw*(h-lh)**3)/3) + ((b1*tf**3)/3)
    Ix = Ix0 - (Ax*yc**2)
    Wel= Ix/((h-lh)-yc)
   
    if Ved <= 0.5*Vpl:
        Mv = fy*Wel*10**(-6)
    else:
        Mv = (fy*Wel)*(1-( (2*Ved/Vpl)-1)**2)*10**(-6)
    if Ved*(tp+ln)*10**(-3) <= Mv:
        return True
    else:
        return False
    
def doubleNotchResistance():
    return

def SingleNotchStability(S,hb,tw,ln,lh):
    #S is steel grade
    #hb is depth of supported beam
    #tw is thickness of web
    #ln is notch length
    #lh is notch depth
    if lh <= 0.5*hb:
        if S == 275:
            if (hb/tw) <= 54.3:
                return ln <= hb
            else:
                return ln <= (1600000*hb)/((hb/tw)**3)
        elif S == 355:
            if hb/tw <= 48:
                return ln <= hb
            else:
                return ln <= (1100000*hb)/((hb/tw)**3)
        else:
            return print("wrong steel grade")
    else:
        return print("Depth of notch is too large")


def DoubleNotchStability(S,lht,lhb,hb,tw,ln):
    if max(lht,lhb) <= 0.2*hb:
        if S == 275:
            if hb/tw <= 54.3:
                return ln <= hb
            else:
                return ln <= (1600000*hb)/((hb/tw)**3)        
        elif S == 355:
            if hb/tw <= 48:
                return ln <= hb
            else:
                return ln <= (1600000*hb)/(hb/tw) 
        else:
            return print("wrong steel grade")

    else:
        return print("Depth of nothc is too large")
    
def boltGroup(Ved,e1,e2,p1,p3,d,d0,n,av,A,tp,fub,fup):
    #e1 end distance
    #e2 edge distance
    #p1 vertical pitch
    #p3 gauges
    #d bolt diameter
    #d0 hole size (22 for M20 bolts)
    #n number of bolts
    #av is 0.6 for 8.8 bolts
    #A is tensile stress area of bolt
    #tp is plate thickness
    #t2 is thickness of supporting 
    #fub ultimate tensile strength of bolt
    #fu2 ultimate strength of supported member
    #b is width of the supporting member
    #w is with of the endplate

    Fv = (av*fub*A)/1.25


    #bearing on end plate
    abp = min(e1/(3*d0),p1/(3*d0)-0.25,fub/fup,1)
    k1p = min(2.8*e2/d0-1.7,1.4*p3/d0-1.7,2.5)
    Fbp = ((k1p*abp*fup*d*tp)/1.25)*10**(-3)

    if Fbp <= 0.8*Fv:
        Frd = n*Fbp
    else:
        Frd = 0.8*n*Fv

    return Ved <= Frd


def endPlateShear(Ved,hp,tp,tw,fyp,n1,d0,fup,p3,e1,e2):
    #hp is the height of the end plate
    #tp is the thickness of the end plate
    #tw is the thicknesss of the supporting web?
    #fyp is the minimum yield strength of the platematerial
    #n1 is number of bolt rows
    #d0 is diameter of the holes
    #p3 is gauge
    #e1 is end distance
    #e2 is edge distance
    

    #Gross section
    Vrdg = ((2*hp*tp)/1.27)*(fyp/(math.sqrt(3)))*10**(-3)

    #Net section
    Av = tp*(hp-(n1*d0))
    Vrdn = 2*Av*(fup/(math.sqrt(3)*1.25))*10**(-3)

    #Block tearing
    Ant = tp*(e2-d0/2)
    Anv = tp*(hp-e1-(n1-0.5)*d0)
    if hp < 1.36*p3 and n1 > 1:
        Vrdb = 2*((0.5*fup*Ant)/(1.25)+(fyp*Anv/math.sqrt(3)))*10**(-3)
    else:
        Vrdb = 2*((fup*Ant)/(1.25)+(fyp*Anv/math.sqrt(3)))*10**(-3)

    Vrdmin = min(Vrdg,Vrdn,Vrdb)

    if hp < 1.36*p3:
        Vrdip = (2*tp*(hp**2)*fyp)/(3*(p3-tw))*10**(-3)
        return Ved <= Vrdmin and Ved <= Vrdip
    else:
        return Ved <= Vrdmin
    

def supportingBeamColumnShearBendingSingle(Ved,t2,e1t,e1b,n1,p1,p3,d,d0,fy2,fum):
    #Ved is design force
    #t2 thickness of the supporting member
    #e1t distance between top of column web and top bolt row
    #e1b distance between bottom of column web and bottom bolt row
    #n1 number of bolt rows
    #p1 vertical pitch between bolts
    #p3 horizontal pitch between bolts
    #d diameter of bolts
    #d0 diameter of bolt holes
    #fy2 yield strength of support element
    #fum ultimate strength of support element
    
    #shear
    et = min(e1t,5*d)
    eb = min(e1b,p3/2,5*d)
    Av = t2*(et+(n1-1)*p1+eb)
    Avnet = Av - n1*d0*t2
    Vrdmin = min((Av*fy2)/math.sqrt(3)*10**(-3),(Avnet*fum)/(1.25*math.sqrt(3))*10**(-3))

    return Ved/2 <= Vrdmin


def plateBoltsTying(Fed,fub,As,dw,N,p3,d0,e1,e2,tw,a,p1,tp,n1,fup):
    #fub is the ultimate tensile strength of the bolt
    #As is the tensile stress area of the bolt (245 for M20)
    #p3 is gauge
    #N is number of bolts
    #dw is the diameter of the washer or the width across points of the bolt or nut as relevant.
    #d0 is the hole diameter
    #e1 is end distance
    #e2 is edge distance
    #a is weld throat thickness
    #p1 is pitch
    #tw is web thickness of supported beam
    #tp is end plate 
    #n1 is the number of bolt rows
    #ultimate strength of the plate

    ew = dw/4
    Ft = 0.9*fub*As/1.1
    m = (p3-tw-(1.6*a*math.sqrt(2)))/2
    n = min(e2,1.25*m)

    if p1 <= p3-tw-2*a*math.sqrt(2)+d0:
        p1A = p1
    else:
        p1A = p3-tw-2*a*math.sqrt(2)+d0

    if e1 <= 0.5*(p3-tw-2*a*math.sqrt(2))+d0/2:
        e1A = e1
    else:
        e1A = 0.5*(p3-tw-2*a*math.sqrt(2))+d0/2

    leff = 2*e1A + (n1-1)*p1A
    Mpl = 0.25*leff*(tp**2)*fup/1.1

    #Mode 1 (complete yielding of the end plate)
    Frd1 = ((8*n-2*ew)*Mpl)/(2*m*n-(ew*(m+n)))*10**(-3) 

    #Mode 2 (bolt failure with yielding of the end plate)
    Frd2 = (2*Mpl+n*(N*Ft))/(m+n)*10**(-3)

    #Mode 3
    Frd3 = N*Ft*10**(-3)

    Frd = min(Frd1,Frd2,Frd3)
    return Fed <= Frd 


def supportedWebTying(Fed,hp,fub,tw):
    #hp is height of plate
    #fub is ultimate strength beam
    #tw is web thickness of supported beam
    Frd = (tw*hp*fub/1.1)*10**(-3)
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

