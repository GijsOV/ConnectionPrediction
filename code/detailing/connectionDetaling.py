class PDEP_INT:
    def __init__(self, material, height, width, thickness, boltRows, boltGauge, boltSize, boltGrade):
        self.material = material
        self.thickness = thickness
        self.height = height   
        self.width = width
        self.boltRows = boltRows
        self.boltGauge = boltGauge
        self.boltSize = boltSize
        self.boltGrade = boltGrade

class FDEP_INT:
    def __init__(self, material, height, width, thickness, boltRows, boltGauge, boltSize, boltGrade):
        self.material = material
        self.thickness = thickness
        self.height = height
        self.width = width
        self.boltRows = boltRows
        self.boltGauge = boltGauge
        self.boltSize = boltSize
        self.boltGrade = boltGrade

class FinPlate_INT:
    def __init__(self, material, height, width, thickness, boltRows, boltGauge, gap, boltSize, boltGrade):
        self.material = material
        self.thickness = thickness
        self.height = height
        self.width = width
        self.boltRows = boltRows
        self.boltGauge = boltGauge
        self.gap = gap
        self.boltSize = boltSize
        self.boltGrade = boltGrade

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
