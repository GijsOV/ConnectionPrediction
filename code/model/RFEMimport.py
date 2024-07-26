import numpy as np
import pandas as pd
from math import comb
from math import acos
from math import pi
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import itertools
import random
import math


##File imports
sectionAreas = pd.read_csv("Info\\typeInfo\\sectionArea.csv")
Materials = pd.read_csv("Info\\typeInfo\\materialInfo.csv")

##LIST OF USED FUNCTIONS
#These functions help with dealing with the data imports from RFEM
#Rounds a string number down to an integer. Used to interpret node and member numbers with one decimal from the RFEM dataset

def roundStr(array,n):
    array = array.astype(str)
    for i in range (0,array.shape[0]):
        N = array[i,n]
        P = N.split('.',2)
        array[i,n] = P[0]
    return array

#Function for splittig string in two arrays using comma separator, used to process cells that contain a list of numbers seperated by comma.
def splitArray(array):
    array = array.astype(str)
    split = [[0,0]]
    for i in range (0,array.shape[0]):
        n = array[i]
        if array[i] != 'nan':
            N = n[0]
            P = N.split(',',2)
            split = np.append(split,[[P[0],P[1]]],axis=0)
        else:
            split = np.append(split,[[0,0]],axis=0)
    split = np.delete(split,0,0)
    split = split.astype(float)
    return split

#Function for inverse comination needed for calculating number of elements at a joint.
def combInv(C):
    n = (1+(1+8*C)**(0.5))/2
    return n

#Function for plotting joints
def plotJoint(Members,Lines,Nodes,Sections,Forces):
    jointNode = nodeList(Members,Lines,Nodes,Sections,Forces)
    memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces) 
    memberPosition = member_Position(Members,Lines,Nodes,Sections,Forces)
    jointNode = jointNode.astype(float)
    nodeInfo = nodeInfo.astype(float)
    fig = plt.figure(figsize = (10,7))
    ax = plt.axes(projection = "3d")
    for i in range (0,jointNode.shape[0]):
        for j in range (0,nodeInfo.shape[0]):
            if jointNode[i,0] == nodeInfo[j,0]:
                ax.scatter3D(nodeInfo[j,1],nodeInfo[j,2],nodeInfo[j,3],color='red')
    for k in range(0,memberPosition.shape[0]):
        ax.plot([memberPosition[k,1],memberPosition[k,4]],[memberPosition[k,2],memberPosition[k,5]],[memberPosition[k,3],memberPosition[k,6]],color='black')
    ax.set_aspect('equal')
    plt.axis('off')
    plt.grid(b=None)
    return plt.show()


#function for calculating magnitude of a vector
def vecMag(vector):
    mag = abs((vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5)
    return mag

#function for calculating the distance between two nodes.
def distance(node1,node2):
    dis = ((node1[0]-node2[0])**2 + (node1[1]-node2[1])**2 + (node1[2]-node2[2])**2)**0.5
    return dis

#function to find if node 3 lies on the line between nodes 1 & 2
def onMember(node1,node2,node3):
    return distance(node1,node3) + distance(node2,node3) == distance(node1,node2)

#function to delete noise in cells for tapered members
def tapered(array):
    array = array.astype(str)
    for i in range (0,array.shape[0]):
        if array[i] != 'nan':
            var = array[i]
            var = var[0]
            var = var.split('}')
            array[i] = var[len(var)-1]
    return array



##IMPORTING DATA
#Creating new arrays with relevant information
def info_array(Members,Lines,Nodes,Sections,Forces):
  memberNo = np.array(Members["Member No"])
  memberLine = np.array(Members["Line No"])
  lineNo = np.array(Lines["Line No"])
  lineNodes= np.array(Lines["Nodes"])
  nodeNo = np.array(Nodes["Node No"])
  nodeX = np.array(Nodes["X"])
  nodeY = np.array(Nodes["Y"])
  nodeZ = np.array(Nodes["Z"])
  sectionName = np.array(Sections["Section Name"])
  sectionMembers = np.array(Sections["Assigned"])
  sectionMaterial = np.array(Sections["Material"])
  forcesMembers = np.array(Forces["Member No"])
  forcesNode = np.array(Forces["Node No"])
  forcesComp = np.array(Forces["NaN"])
  forcesN = np.array(Forces["N"])
  forcesVy = np.array(Forces["Vy"])
  forcesVz = np.array(Forces["Vz"])
  forcesMt = np.array(Forces["Mt"])
  forcesMy = np.array(Forces["My"])
  forcesMz = np.array(Forces["Mz"])

  #Deleting first two elements
  memberNo = np.delete(memberNo, [0,1])
  memberLine = np.delete(memberLine, [0,1])
  lineNo = np.delete(lineNo, [0,1])
  lineNodes = np.delete(lineNodes, [0,1])
  nodeNo = np.delete(nodeNo, [0,1])
  nodeX = np.delete(nodeX, [0,1])
  nodeY = np.delete(nodeY, [0,1])
  nodeZ = np.delete(nodeZ, [0,1])
  sectionName = np.delete(sectionName, [0,1])
  sectionMembers = np.delete(sectionMembers, [0,1])
  sectionMaterial = np.delete(sectionMaterial, [0,1])
  forcesMembers = np.delete(forcesMembers, [0,1])
  forcesNode = np.delete(forcesNode, [0,1])
  forcesComp = np.delete(forcesComp, [0,1])
  forcesN = np.delete(forcesN, [0,1])
  forcesVy = np.delete(forcesVy, [0,1])
  forcesVz = np.delete(forcesVz, [0,1])
  forcesMt = np.delete(forcesMt, [0,1])
  forcesMy = np.delete(forcesMy, [0,1])
  forcesMz = np.delete(forcesMz, [0,1])

  #Reshaping
  memberNo = memberNo.reshape(memberNo.shape[0],1)
  memberLine = memberLine.reshape(memberLine.shape[0],1)
  lineNo = lineNo.reshape(lineNo.shape[0],1)
  lineNodes = lineNodes.reshape(lineNodes.shape[0],1)
  lineNode1 = splitArray(lineNodes)[:,0].reshape(lineNodes.shape[0],1)
  lineNode2 = splitArray(lineNodes)[:,1].reshape(lineNodes.shape[0],1)
  nodeNo = nodeNo.reshape(nodeNo.shape[0],1)
  nodeX = nodeX.reshape(nodeX.shape[0],1)
  nodeY = nodeY.reshape(nodeY.shape[0],1)
  nodeZ = nodeZ.reshape(nodeZ.shape[0],1)
  sectionName = sectionName.reshape(sectionName.shape[0],1)
  sectionMembers = sectionMembers.reshape(sectionMembers.shape[0],1)
  sectionMaterial = sectionMaterial.reshape(sectionMaterial.shape[0],1)
  sectionMembers = tapered(sectionMembers)
  forcesMembers = forcesMembers.reshape(forcesMembers.shape[0],1)
  forcesComp = forcesComp.reshape(forcesComp.shape[0],1)
  forcesNode = forcesNode.reshape(forcesNode.shape[0],1)
  forcesN = forcesN.reshape(forcesN.shape[0],1)
  forcesVy = forcesVy.reshape(forcesVy.shape[0],1)
  forcesVz = forcesVz.reshape(forcesVz.shape[0],1)
  forcesMt = forcesMt.reshape(forcesMt.shape[0],1)
  forcesMy = forcesMy.reshape(forcesMy.shape[0],1)
  forcesMz = forcesMz.reshape(forcesMz.shape[0],1)
  ##CREATING INFORMATION ARRAYS

  #creating arrays with memberInfo (memberNumber memberLine), lineInfo(lineNumber startNode endNode), nodeInfo(nodeNumber XYZ postion)
  memberInfo = np.concatenate((memberNo,memberLine),axis=1)
  lineInfo = np.concatenate((lineNo,lineNode1,lineNode2),axis=1)
  nodeInfo = np.concatenate((nodeNo,nodeX,nodeY,nodeZ),axis=1)
  sectionInfo = np.concatenate((sectionMembers,sectionMaterial,sectionName),axis=1)
  forcesInfo = np.concatenate((forcesMembers,forcesNode,forcesComp,forcesN,forcesVy,forcesVz,forcesMt,forcesMy,forcesMz),axis=1)
  return memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo

#creating array with rows containing member number and its start and end node [memberNo,node1,node2]
def member_Nodes(Members,Lines,Nodes,Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  Len = memberInfo[:,0].reshape(memberInfo.shape[0],1)
  memberNodes=np.concatenate((Len,Len,Len),axis=1)
  memberInfo = memberInfo.astype(float)
  lineInfo = lineInfo.astype(float)
  for i in range(0,memberInfo.shape[0]):
      for j in range (0,lineInfo.shape[0]):
          if memberInfo[i,1]==lineInfo[j,0]:
              memberNodes[i,1]=lineInfo[j,1]
              memberNodes[i,2]=lineInfo[j,2]
  return memberNodes

#creating array with rows containing member number and its start and end position [memberNo,startXYZ,endXYZ]
def member_Position(Members,Lines,Nodes,Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  memberNodes = member_Nodes(Members,Lines,Nodes,Sections,Forces)
  Len = memberInfo[:,0].reshape(memberInfo.shape[0],1)
  memberPosition=np.concatenate((Len,Len,Len,Len,Len,Len,Len),axis=1)
  nodeInfo = nodeInfo.astype(float)
  memberNodes = memberNodes.astype(float)
  for i in range (0,memberNodes.shape[0]):
      for j in range(0,nodeInfo.shape[0]):
          if memberNodes[i,1] == nodeInfo[j,0]:
              memberPosition[i,1]=nodeInfo[j,1]
              memberPosition[i,2]=nodeInfo[j,2]
              memberPosition[i,3]=nodeInfo[j,3]
          if memberNodes[i,2] == nodeInfo[j,0]:
              memberPosition[i,4]=nodeInfo[j,1]
              memberPosition[i,5]=nodeInfo[j,2]
              memberPosition[i,6]=nodeInfo[j,3]
  return memberPosition

#creating array with rows conainting line number and its start and end position [lineNo startXYZ endXYZ]
def line_Position(Members,Lines,Nodes, Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  Len = lineInfo[:,0].reshape(lineInfo.shape[0],1)
  linePosition=np.concatenate((Len,Len,Len,Len,Len,Len,Len),axis=1)
  lineInfo = lineInfo.astype(float)
  nodeInfo = nodeInfo.astype(float)
  for i in range (0,lineInfo.shape[0]):
      for j in range(0,nodeInfo.shape[0]):
          if lineInfo[i,1] == nodeInfo[j,0]:
              linePosition[i,1]=nodeInfo[j,1]
              linePosition[i,2]=nodeInfo[j,2]
              linePosition[i,3]=nodeInfo[j,3]
          if lineInfo[i,2] == nodeInfo[j,0]:
              linePosition[i,4]=nodeInfo[j,1]
              linePosition[i,5]=nodeInfo[j,2]
              linePosition[i,6]=nodeInfo[j,3]
  linePosition = linePosition.astype(float)
  return linePosition

#creating an array with nodes that lie on a a member 
def onMember_Node(Members,Lines,Nodes, Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  linePosition = line_Position(Members,Lines,Nodes, Sections,Forces)
  memberInfo = memberInfo.astype(float)
  onMemberNode = [[0,0]]
  lineInfo = lineInfo.astype(float)
  nodeInfo = nodeInfo.astype(float)
  for i in range (0,linePosition.shape[0]):
      for j in range (0,nodeInfo.shape[0]):
          if lineInfo[i,2] != nodeInfo[j,0] and lineInfo[i,1] != nodeInfo[j,0] and onMember(linePosition[i,1:4],linePosition[i,4:7],nodeInfo[j,1:4]):
            for k in range (memberInfo.shape[0]):
                if memberInfo[k,1] == linePosition[i,0]:
                    onMemberNode = np.append(onMemberNode,[[nodeInfo[j,0],memberInfo[k,0]]],axis=0)
  onMemberNode = np.delete(onMemberNode,0,0)
  return onMemberNode

#assigning material to member info
def memberInfoMat(Members,Lines,Nodes, Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  memberInfo = memberInfo.astype(float)
  memberInfo = np.c_[memberInfo,np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0])]
  memberInfo = memberInfo.astype(str)
  sectionInfo = sectionInfo.astype(str)
  for i in range (0,sectionInfo.shape[0]):
      if sectionInfo[i,0] != 'nan':
          var = sectionInfo[i,0]
          var = var.split(',')
          for j in range (0,len(var)):
              n = var[j]
              N = n.split('-')
              if len(N) == 1:
                  a = int(N[0])
                  memberInfo[a-1,2] = sectionInfo[i,1]
                  memberInfo[a-1,3] = sectionInfo[i,2]
              if len(N) == 2:
                  a = int(N[0])
                  b = int(N[1])
                  for k in range (a,b+1):
                      memberInfo[(k-1),2] = sectionInfo[i,1]
                      memberInfo[(k-1),3] = sectionInfo[i,2]
  return memberInfo

#Add internal forces to memberInfo (memberno, lineno, material, node1 forces xyz mxmymz, node2 forces xyz mxmymz)
def memberInfoForce(Members,Lines,Nodes, Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  memberInfo = memberInfoMat(Members,Lines,Nodes, Sections,Forces)
  memberInfo = np.c_[memberInfo,np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0]),np.ones(memberInfo.shape[0])]
  key = 0
  pasw = 1
  for i in range (0,forcesInfo.shape[0]):
      if forcesInfo[i,0] == forcesInfo[i-1,0]:
          pasw = int(forcesInfo[i,0])
          if pasw != key and pasw > key:
              for j in range (0,memberInfo.shape[0]):
                  a = forcesInfo[i,0]
                  b = memberInfo[j,0]
                  A = b.split('.',2)
                  B = a.split('.',2)
                  if A[0] == B[0]:
                      memberInfo[j,4] = forcesInfo[i-1,1]
                      memberInfo[j,5] = forcesInfo[i-1,3]
                      memberInfo[j,6] = forcesInfo[i-1,4]
                      memberInfo[j,7] = forcesInfo[i-1,5]
                      memberInfo[j,8] = forcesInfo[i-1,6]
                      memberInfo[j,9] = forcesInfo[i-1,7]
                      memberInfo[j,10] = forcesInfo[i-1,8]
                      memberInfo[j,11] = forcesInfo[i,1]          
                      memberInfo[j,12] = forcesInfo[i,3]
                      memberInfo[j,13] = forcesInfo[i,4]
                      memberInfo[j,14] = forcesInfo[i,5]
                      memberInfo[j,15] = forcesInfo[i,6]
                      memberInfo[j,16] = forcesInfo[i,7]
                      memberInfo[j,17] = forcesInfo[i,8]
              key = pasw
  return memberInfo

#Memberforces list. [memberNo, nodeNo, Forces]
def memberForceList(Members,Lines,Nodes, Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  memberInfo = memberInfoForce(Members,Lines,Nodes, Sections,Forces)
  memberForces = [[0,0,0,0,0,0,0,0]]
  forcesInfo = forcesInfo.astype(str)
  for i in range (0,memberInfo.shape[0]):
      nodeList = ['nan']
      for j in range (0,forcesInfo.shape[0]):
          p = forcesInfo[j,0]
          o = memberInfo[i,0]
          P = p.split('.',2)
          O = o.split('.',2)
          if O[0] == P[0]:
              if forcesInfo[j,1] not in nodeList:
                  nodeList = np.append(nodeList,[[forcesInfo[j,1]]])
                  memberForces = np.append(memberForces,[[memberInfo[i,0],forcesInfo[j,1],forcesInfo[j,3],forcesInfo[j,4],forcesInfo[j,5],forcesInfo[j,6],forcesInfo[j,7],forcesInfo[j,8]]],axis=0)
  memberForces = np.delete(memberForces,0,0)
  return memberForces



##JOINT RECOGNITION
#creating a list of nodes where 2 members join represented by the node, and the two members that join [node, member 1, member 2, onmember 0=no 1=yes]
def findJoint(Members,Lines,Nodes,Sections,Forces):
  memberPosition = member_Position(Members,Lines,Nodes,Sections,Forces)
  memberNodes = member_Nodes(Members,Lines,Nodes,Sections,Forces)
  onMemberNode = onMember_Node(Members,Lines,Nodes,Sections,Forces)
  nodeJoint = [[0,0,0,0,0]]
  memberPosition = memberPosition.astype(float)
  for i in range (0,memberNodes.shape[0]):
      for k in range(onMemberNode.shape[0]):
              if memberNodes[i,1] == onMemberNode[k,0]:
                  nodeJoint = np.append(nodeJoint,[[memberNodes[i,1],memberNodes[i,0],onMemberNode[k,1],1,1]],axis=0)
              if memberNodes[i,2] == onMemberNode[k,0]:
                  nodeJoint = np.append(nodeJoint,[[memberNodes[i,2],memberNodes[i,0],onMemberNode[k,1],1,1]],axis=0)
      for j in range (i+1,memberNodes.shape[0]):
          if memberNodes[i,1]==memberNodes[j,1]:
              nodeJoint = np.append(nodeJoint,[[memberNodes[i,1], memberNodes[i,0],memberNodes[j,0],0,0]],axis=0)
          if memberNodes[i,1]==memberNodes[j,2]:
              nodeJoint = np.append(nodeJoint,[[memberNodes[i,1], memberNodes[i,0],memberNodes[j,0],0,0]],axis=0)
          if memberNodes[i,2]==memberNodes[j,1]:
              nodeJoint = np.append(nodeJoint,[[memberNodes[i,2], memberNodes[i,0],memberNodes[j,0],0,0]],axis=0)
          if memberNodes[i,2]==memberNodes[j,2]:
              nodeJoint = np.append(nodeJoint,[[memberNodes[i,2], memberNodes[i,0],memberNodes[j,0],0,0]],axis=0)
  nodeJoint = np.delete(nodeJoint,0,0)
  return nodeJoint

#creating a list of joints including number of elements [node numberOfElements]
def nodeList(Members,Lines,Nodes,Sections,Forces):
  memberInfo,lineInfo,nodeInfo,sectionInfo,forcesInfo = info_array(Members,Lines,Nodes, Sections,Forces)
  nodeJoint = findJoint(Members,Lines,Nodes,Sections,Forces)
  nodeJoint = nodeJoint.astype(float)
  nodeInfo = nodeInfo.astype(float)
  jointNode = [[0,0]]
  for i in range (0,nodeInfo.shape[0]):
      index = np.where(nodeJoint[:,0] == nodeInfo[i,0])[0]
      index = index.shape[0]
      if index > 0: 
          jointNode = np.append(jointNode,[[nodeInfo[i,0],combInv(index)]],axis=0)
  jointNode = np.delete(jointNode,0,0)
  return jointNode

#finding angle between elements for each connection [node member1 member2 angle] 
def findAngle(Members,Lines,Nodes,Sections,Forces):
  memberNodes = member_Nodes(Members,Lines,Nodes,Sections,Forces)
  nodeJoint = findJoint(Members,Lines,Nodes,Sections,Forces)
  memberPosition = member_Position(Members,Lines,Nodes,Sections,Forces)
  nodeJoint = nodeJoint.astype(float)
  jointAngle = nodeJoint
  for i in range (0,jointAngle.shape[0]):
      memA = jointAngle[i,1]-1
      memB = jointAngle[i,2]-1
      memA = memA.astype(int)
      memB = memB.astype(int)

      if jointAngle[i,0] == memberNodes[memA,2]:
          vecA = np.array([memberPosition[memA,1]-memberPosition[memA,4],memberPosition[memA,2]-memberPosition[memA,5],memberPosition[memA,3]-memberPosition[memA,6]])
      else:
          vecA = np.array([memberPosition[memA,4]-memberPosition[memA,1],memberPosition[memA,5]-memberPosition[memA,2],memberPosition[memA,6]-memberPosition[memA,3]])
      if jointAngle[i,0] == memberNodes[memB,2]:
          vecB = np.array([memberPosition[memB,1]-memberPosition[memB,4],memberPosition[memB,2]-memberPosition[memB,5],memberPosition[memB,3]-memberPosition[memB,6]])
      else:
          vecB = np.array([memberPosition[memB,4]-memberPosition[memB,1],memberPosition[memB,5]-memberPosition[memB,2],memberPosition[memB,6]-memberPosition[memB,3]])
      
      angle = acos(np.dot(vecA,vecB)/(vecMag(vecA)*vecMag(vecB)))
      jointAngle[i,3] = angle*(180/pi)
  return jointAngle





def orientations(Members,Lines,Nodes,Sections,Forces):
    jointAngle = findAngle(Members,Lines,Nodes,Sections,Forces)
    joints = jointAngle.astype(int)
    joints = joints.astype(str)
    jointsPosition = joints[:,1:]
    jointsRotation = np.zeros_like(jointsPosition)
    jointsRotation[:,:2] = jointsPosition[:,:2]
    memberPosition = np.array(Members["Position"])
    memberNumber = np.array(Members["Member No"])
    memberRotation = np.array(Members["Rotation"])

    memberPosition = np.delete(memberPosition, [0,1])
    memberNumber = np.delete(memberNumber, [0,1])
    memberRotation = np.delete(memberRotation, [0,1])

    memberPosition = memberPosition.reshape(memberPosition.shape[0],1)
    memberNumber = memberNumber.reshape(memberNumber.shape[0],1)
    memberRotation = memberRotation.reshape(memberRotation.shape[0],1)
   
    position = np.concatenate((memberNumber,memberPosition),axis=1)
    rotation = np.concatenate((memberNumber,memberRotation),axis=1)

  
    for i in range (0,jointsPosition.shape[0]):
        for j in range (0,position.shape[0]):
            if jointsPosition[i,0] == position[j,0]:
                jointsPosition[i,2] = position[j,1]
            if jointsPosition[i,1] == position[j,0]:
                jointsPosition[i,3] = position[j,1]

    for i in range (0,jointsPosition.shape[0]):
        for j in range (0,rotation.shape[0]):
            if jointsPosition[i,0] == rotation[j,0]:
                jointsRotation[i,2] = rotation[j,1]
            if jointsPosition[i,1] == rotation[j,0]:
                jointsRotation[i,3] = rotation[j,1]  

    for i in range (0,jointsPosition.shape[0]):
        if jointsPosition[i,2] == 'On Z' or jointsPosition[i,2] == '|| Z':
            jointsPosition[i,2] = 'Z'
        elif jointsPosition[i,2] == 'On Y' or jointsPosition[i,2] == '|| Y':
            jointsPosition[i,2] = 'Y'
        elif jointsPosition[i,2] == 'On X' or jointsPosition[i,2] ==  '|| X':
            jointsPosition[i,2] = 'X'
        elif jointsPosition[i,2] == 'In XY' or jointsPosition[i,2] ==  '|| XY':
            jointsPosition[i,2] = 'XY'
        elif jointsPosition[i,2] == 'In XZ' or jointsPosition[i,2] ==  '|| XZ':
            jointsPosition[i,2] = 'XZ'
        elif jointsPosition[i,2] == 'In YZ' or jointsPosition[i,2] ==  '|| YZ':
            jointsPosition[i,2] = 'YZ'           

        if jointsPosition[i,3] == 'On Z' or jointsPosition[i,3] == '|| Z':
            jointsPosition[i,3] = 'Z'
        elif jointsPosition[i,3] == 'On Y' or jointsPosition[i,3] == '|| Y':
            jointsPosition[i,3] = 'Y'
        elif jointsPosition[i,3] == 'On X' or jointsPosition[i,3] ==  '|| X':
            jointsPosition[i,3] = 'X'
        elif jointsPosition[i,3] == 'In XY' or jointsPosition[i,3] ==  '|| XY':
            jointsPosition[i,3] = 'XY'
        elif jointsPosition[i,3] == 'In XZ' or jointsPosition[i,3] ==  '|| XZ':
            jointsPosition[i,3] = 'XZ'
        elif jointsPosition[i,3] == 'In YZ' or jointsPosition[i,3] ==  '|| YZ':
            jointsPosition[i,3] = 'YZ'    
    return jointsRotation,jointsPosition





#Change material to yield strength and change section to I,H,F for I hollow or flat
#add area column that descripes sectional area

#supported element first supporting element second.


#Try to locate the right design force using orientationl.

def sections(memberInfo):
    sectionInfo = np.zeros((memberInfo.shape[0],3))
    sectionInfo[:,0] = memberInfo[:,0]
    sectionInfo = sectionInfo.astype(int)
    sectionInfo = sectionInfo.astype(str)
    for i in range (0,memberInfo.shape[0]):
        for j in range (0,sectionAreas.shape[0]):
            if memberInfo[i,3] == sectionAreas.loc[j,'Section']:
                sectionInfo[i,1] = sectionAreas.loc[j,'Type']
                sectionInfo[i,2] = sectionAreas.loc[j,'A']
    return sectionInfo


def materials(memberInfo):
    materialInfo = np.zeros((memberInfo.shape[0],2))
    materialInfo[:,0] = memberInfo[:,0]
    materialInfo = materialInfo.astype(int)
    materialInfo = materialInfo.astype(str)
    for i in range (0,memberInfo.shape[0]):
        for j in range (0,Materials.shape[0]):
            if memberInfo[i,2] == Materials.loc[j,'Material ']:
                materialInfo[i,1] = Materials.loc[j,'fy']

    return materialInfo



def supporting(input):
    #check both Z, large area supporting
    #elif M1 is Z, M1 is supporting
    #elif M2 is Z, M2 is supporting
    #elif, large area supporting

    support = np.ones((input.shape[0],1))

    JA = input[:,3].astype(float)
    input[:,3] = np.round(JA).astype(float)
    JA = input[:,8].astype(float)
    input[:,8] = np.round(JA).astype(float)

    for i in range(input.shape[0]):
        if input[i,4] == 'Z' and input[i,9] == 'Z':
            if np.less_equal(input[i,3],input[i,8]):
                support[i,0] = 1
            else:
                support[i,0] = 0
        elif input[i,4] == 'Z' and input[i,9] != 'Z':
            support[i,0] = 1
        elif input[i,4] != 'Z' and input[i,9] == 'Z':
            support[i,0] = 0
        elif input[i,4] !='Z' and input[i,9] != 'Z':
            if np.less_equal(input[i,3],input[i,8]):
                support[i,0] = 1
            else:
                support[i,0] = 0
    return support



#Creating input data array (MemberInfo 1, MemberInfo 2, Angle, Forces 1, Forces 2) represents all connections, same shape as jointAngle
#might need a way to identify the connection to label the output data
def inputData(Members,Lines,Nodes, Sections,Forces):
  memberInfo = memberInfoForce(Members,Lines,Nodes, Sections,Forces)
  jointAngle = findAngle(Members,Lines,Nodes,Sections,Forces)
  memberForces = memberForceList(Members,Lines,Nodes, Sections,Forces)
  jointAngle = jointAngle.astype(str)
  input = np.ones((jointAngle.shape[0],32))
  jointAngle = roundStr(jointAngle,0)
  rot,pos = orientations(Members,Lines,Nodes,Sections,Forces)
  sec = sections(memberInfo)
  mat = materials(memberInfo)


  MF = memberForces[:,0].astype(float)
  memberForces[:,0] = np.round(MF).astype(int)
  memberForces[:,0] = memberForces[:,0].astype(str)
  
  JA = jointAngle[:,1].astype(float)
  jointAngle[:,1] = np.round(JA).astype(int)
  jointAngle[:,1] = jointAngle[:,1].astype(str)
  
  JA2 = jointAngle[:,2].astype(float)
  jointAngle[:,2] = np.round(JA2).astype(int)
  jointAngle[:,2] = jointAngle[:,2].astype(str)
  
  MI = memberInfo[:,0].astype(float)
  memberInfo[:,0] = np.round(MI).astype(int)
  memberInfo[:,0] = memberInfo[:,0].astype(str)
  
  MI = memberInfo[:,1].astype(float)
  memberInfo[:,1] = np.round(MI).astype(int)
  memberInfo[:,1] = memberInfo[:,1].astype(str)
  input = input.astype(str)


  input[:,0] = jointAngle[:,1] #member1
  input[:,5] = jointAngle[:,2] #member2
  input[:,10] = jointAngle[:,3] #Angle
  input[:,4] = pos[:,2]
  input[:,9] = pos[:,3]
    	

  for i in range (0,jointAngle.shape[0]):
      for j in range (0,memberInfo.shape[0]):
          if jointAngle[i,1] == memberInfo[j,0]: #member 1 info, find node of member
              input[i,1] = mat[j,1]
              input[i,2] = sec[j,1]
              input[i,28] = memberInfo[j,3]
              input[i,30] = memberInfo[j,2]
          if jointAngle[i,2] == memberInfo[j,0]: #member 2 info, find node of member
              input[i,6] = mat[j,1]
              input[i,7] = sec[j,1]
              input[i,29] = memberInfo[j,3]
              input[i,31] = memberInfo[j,2]
      for k in range (0,memberForces.shape[0]):
          if jointAngle[i,1] == memberForces[k,0]:
              for l in range (0,memberForces.shape[0]):
                  if jointAngle[i,0] == memberForces[l,1] and jointAngle[i,1] == memberForces[l,0]:
                      input[i,11] = memberForces[l,2] 
                      input[i,12] = memberForces[l,3]    
                      input[i,13] = memberForces[l,4] 
                      input[i,14] = memberForces[l,5] 
                      input[i,15] = memberForces[l,6] 
                      input[i,16] = memberForces[l,7]             
          if jointAngle[i,2] == memberForces[k,0]:
              for l in range (0,memberForces.shape[0]):
                  if jointAngle[i,0] == memberForces[l,1] and jointAngle[i,2] == memberForces[l,0]:
                      input[i,17] = memberForces[l,2] 
                      input[i,18] = memberForces[l,3]    
                      input[i,19] = memberForces[l,4] 
                      input[i,20] = memberForces[l,5] 
                      input[i,21] = memberForces[l,6] 
                      input[i,22] = memberForces[l,7]
      for l in range (0,sec.shape[0]):
          if jointAngle[i,1] == sec[l,0]:
              input[i,3] = sec[l,2]
          if jointAngle[i,2] == sec[l,0]:
              input[i,8] = sec[l,2]
            

  for i in range (0,input.shape[0]):
      input[i,24] = rot[i,2]
      input[i,25] = rot[i,3]
  

  support = supporting(input)
  for i in range (0, support.shape[0]):
      if support[i] == 0:
          input[i,0:5], input[i,5:10] = input[i,5:10], input[i,0:5].copy()
          input[i,11:17], input[i,17:23] = input[i,17:23], input[i,11:17].copy()
          input[i,24],input[i,25] = input[i,25],input[i,24].copy()
          input[i,28:30],input[i,30:32] = input[i,30:32],input[i,28:30].copy()

  for i in range (0,input.shape[0]):
      if input[i,2] == 'I':
         if input[i,4] == 'Z' and input[i,24] == '0.00' and (input[i,9] == 'X' or input[i,9] == 'XZ' or input[i,9] == 'XY'):
             input[i,23] = 0
         elif input[i,4] == 'Z' and input[i,24] == '0.00' and (input[i,9] == 'Y' or input[i,9] == 'YZ'):
             input[i,23] = 1
         elif input[i,4] == 'Z' and input[i,24] == '90.00' and (input[i,9] == 'X' or input[i,9] == 'XZ'):
             input[i,23] = 1
         elif input[i,4] == 'Z' and input[i,24] == '90.00' and (input[i,9] == 'Y' or input[i,9] == 'YZ' or input[i,9] == 'XY'):
             input[i,23] = 0
         elif input[i,4] == 'Z' and input[i,9] == 'Z':
             input[i,23] = 3

         elif input[i,4] == 'X' and input[i,24] == '0.00' and (input[i,9] == 'Y' or input[i,9] == 'XY' or input[i,9] =='YZ'):
             input[i,23] = 1
         elif input[i,4] == 'X' and input[i,24] == '0.00' and (input[i,9] == 'Z' or input[i,9] == 'XZ'):
             input[i,23] = 0
         elif input[i,4] == 'X' and input[i,24] == '90.00' and (input[i,9] == 'Y' or input[i,9] == 'XY'):
             input[i,23] = 0
         elif input[i,4] == 'X' and input[i,24] == '90.00' and (input[i,9] == 'Z' or input[i,9] == 'XZ' or input[i,9] =='YZ'):
             input[i,23] = 1
         elif input[i,4] == 'X' and input[i,9] == 'X':
             input[i,23] = 3
         
         elif input[i,4] == 'Y' and input[i,24] == '0.00' and (input[i,9] == 'X' or input[i,9] == 'XY' or input[i,9] =='XZ'):
             input[i,23] = 1
         elif input[i,4] == 'Y' and input[i,24] == '0.00' and (input[i,9] == 'Z' or input[i,9] == 'YZ'):
             input[i,23] = 0
         elif input[i,4] == 'Y' and input[i,24] == '90.00' and (input[i,9] == 'X' or input[i,9] == 'XY'):
             input[i,23] = 0
         elif input[i,4] == 'Y' and input[i,24] == '90.00' and (input[i,9] == 'Z' or input[i,9] == 'YZ' or input[i,9] =='XZ'):
             input[i,23] = 1
         elif input[i,4] == 'Y' and input[i,9] == 'Y':
             input[i,23] = 3

      elif input[i,2] != 'I':
        input[i,23] = 2


  for i in range (0, input.shape[0]):
      if input[i,9] != 'Z':
        if input[i,25] == '0.00':
            input[i,26] = abs(input[i,19].astype(float))
        elif input[i,25] != '0.00':
            input[i,26] = abs(input[i,18].astype(float))
      
      input[i,27] = abs(input[i,17].astype(float))
  

  columns_to_remove = [0, 5] + list(range(11, 23)) + [24, 25]
  input = np.delete(input, columns_to_remove, axis=1)

  return input











#transform input/output numpy array to a pandas dataframe. Clear distinction between floats and obejcts.
def rfInput (input,output):
  input1 = np.c_[input[:,0:12],output]
  input2 = input[:,12:16]
  input[:,0] = input[:,0].astype(float)
  inputpd = pd.DataFrame(input1,columns = ['Material1','Section1','Area1','Orientation1','Material2','Section2','Area2','Orientation2','Angle','W/F/H','Ved','Fed','Output'])
  inputpd = inputpd.astype({'Output' : 'float'})
  inputpd = inputpd.astype({'Material1' : 'float'})
  inputpd = inputpd.astype({'Material2' : 'float'})
  inputpd = inputpd.astype({'Area1' : 'float'})
  inputpd = inputpd.astype({'Area2' : 'float'})
  inputpd = inputpd.astype({'Angle' : 'float'})
  inputpd = inputpd.astype({'Ved' : 'float'})
  inputpd = inputpd.astype({'Fed' : 'float'})
  
  inputInfo = pd.DataFrame(input2,columns = ['supportingSection','supportedSection','supportingMaterial','supportedMaterial'])
  return inputpd,inputInfo

def toCsv(dataframe, filename):
    dataframe.to_csv(filename, index= False)


#def function for identifying double sided connections.
#find connection node, find opposite orientation? should work with inplane aswell.