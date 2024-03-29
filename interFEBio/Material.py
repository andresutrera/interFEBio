"""
This module is related to material definition.
"""

import xml.etree.cElementTree as ET
from .dataClass import _var,sectionAttribs


class material():
    def __init__(self,id:int|str = 1, name:str = None, type:str = None,elementSet:str = None, parameters:dict = None, attributes:dict = None):

        self.id = id
        self.type = type
        self.name = name
        self.elementSet=elementSet
        #self.attributes = attributes
        self.atr = sectionAttribs()

        for param,value in parameters.items():
            #print("at material class: ",param)
            if(isinstance(value,materialBranch)):
                #print("at material class, is branch: ",param)
                value.branchType=param
                self.atr.addAttrib(value) 
            else:
                #print("at material class, is param: ",param)
                self.atr.addAttrib(_var(param,value,attributes) ) 

    def tree(self):
        tree = ET.Element('material', id=str(self.id), name=self.name, type=self.type)
        self.atr.fillTree(tree)
        return tree

    def addParam(self,parameter=None,attributes=None):
        for param,value in parameter.items():
            #print("at material class: ",param)
            if(isinstance(value,materialBranch)):
                #print("at material class, is branch: ",param)
                value.branchType=param
                self.atr.addAttrib(value) 
            else:
                #print("at material class, is param: ",param)
                self.atr.addAttrib(_var(param,value,attributes) )       

class materialBranch():
    def __init__(self,type:str = None,parameters:dict = None, attributes:dict = None):

        #self.branchType = branchType
        self.type = type
        #self.attributes = attributes
        self.atr = sectionAttribs()

        for param,value in parameters.items():
            if(isinstance(value,materialBranch)):
                value.branchType=param
                self.atr.addAttrib(value)
            else:
                self.atr.addAttrib(_var(param,value,attributes) ) 
        
    def tree(self):
        tree = ET.Element(self.branchType, type=self.type)
        self.atr.fillTree(tree)

        

        return tree


class Material():
    '''
    Define a material object associated to a particular list of element sets.

    Args:
    ----------

        mtype(str)          : Name of the material model.

        elsets(list/str)    : Name of the element sets associated to this material.

        mname(str)          : Material name.

        matid(int)          : Material ID.

        subattributes(dict) : Subattributes of the material (type, lc, etc...)

    '''

    def __init__(self,material:material = None):
        self.baseMat = material
    
    def tree(self):
        tree = ET.Element('Material')
        tree.append(self.baseMat.tree())
        return tree        
        
