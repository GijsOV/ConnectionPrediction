import numpy as np
import pandas as pd
import math
class GussetPlate_INT:
    def __init__(self, material, height, width, thickness, boltRows, boltGauge, angle, gap, boltSize, boltGrade):
        self.material = material
        self.height = height
        self.width = width
        self.thickness = thickness
        self.boltRows = boltRows
        self.boltGauge = boltGauge
        self.angle = angle
        self.gap = gap
        self.boltSize = boltSize
        self.boltGrade = boltGrade

sectionInfo = pd.read_csv("Info/dataTrain/IsectionInfo.csv")
data = pd.read_csv("Info/dataTrain/data.csv")
dataInfo = pd.read_csv("Info/dataTrain/data_Info.csv")

joint = data.loc[202]

Info = dataInfo.loc[202]



def GussetPlate(joint,jointInfo):
    g, tp, n1, p3 = 500, 10, 2, 70
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
        connection = GussetPlate_INT('S275',hp,wp,tp,n1,p3,angle,g,20,88)
    else:
        section = sectionInfo[sectionInfo['Section'] == jointInfo['supportingSection']]
        angle = round(joint['Angle'])
        hb = 0.5*section.iloc[0]['A']
        wp = float(abs(g*math.cos(angle)))
        hp = float(abs(g*math.sin(angle)-hb))
        connection = GussetPlate_INT('S275',hp,wp,tp,n1,p3,angle,g,20,88)
    return connection

