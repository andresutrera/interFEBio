"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
import xml.etree.cElementTree as ET
from dataClass import _var,sectionAttribs
import Boundary,Loads,Contact,Control,Rigid

class Step():
    def __init__(self,
                 id : int = 1,
                 name : str = 'Step1',
                 ):

        self.id = id
        self.name = name

        self.atr = sectionAttribs()

        self.bndatr = []
        self.loadsatr = []
        self.rigidatr = []
        self.contacatr = []
        # self.atr.addAttrib(Control)
        # self.atr.addAttrib(Boundary)
        # self.atr.addAttrib(Loads )
        # self.atr.addAttrib(Contact )

    def addControl(self,ctrl: Control = Control.Control()):
        self.atr.addAttrib(ctrl)
    def addBoundary(self,bound: Boundary = None):
        self.bndatr.append(bound)
    def addLoad(self,load: Loads = None):
        self.loadsatr.append(load)
    def addRigid(self,rigid: Rigid = None):
        self.rigidatr.append(rigid)
    def addContact(self,cntc: Contact = None):
        self.contacatr.append(cntc)
    
    

    def tree(self):
        tree = ET.Element('step', id=str(self.id), name=self.name)
        self.atr.fillTree(tree)
        bndTree = ET.Element('Boundary')
        for item in self.bndatr:
            bndTree.append(item.tree())
        tree.append(bndTree)

        loadsTree = ET.Element('Loads')
        for item in self.loadsatr:
            loadsTree.append(item.tree())
        tree.append(loadsTree)

        rigidTree = ET.Element('Rigid')
        for item in self.rigidatr:
            rigidTree.append(item.tree())
        tree.append(rigidTree)

        contactTree = ET.Element('Contact')
        for item in self.contacatr:
            contactTree.append(item.tree())
        tree.append(contactTree)

        return tree
    
