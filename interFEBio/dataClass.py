"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
from dataclasses import dataclass
from typing import Optional,Union
import xml.etree.cElementTree as ET

@dataclass
class _var():
    name : str
    value : Union[int,float,bool,str,list]
    attrib : Optional[dict] = None
    ###

    def __post_init__(self):
        if self.attrib is not None:
            self.attrib = self.attrib.get(self.name)

    def varTree(self):
        Etree = ET.Element(self.name)

        Etree.text = str(self.value)
        if(self.attrib is not None):
            for att in self.attrib:
                Etree.set(att, str(self.attrib[att]))
        return Etree
    

class sectionAttribs():
    def __init__(self):
        self.attribs = {}

    def addAttrib(self,var :_var = None):
        if isinstance(var,_var):
            self.attribs[var.name] = var
        else:
            #self.attribs[str(type(var))] = var
            #self.attribs[var.type] = var
            self.attribs[id(var)] = var

    def fillTree(self,tree):
        for item in self.attribs.values():
            #print("At dataClass: ",item)
            if isinstance(item,_var):
                #print("At dataClass: is var ",item)
                tree.append(item.varTree())
            else:
                #print("At dataClass: is branch ",item)
                tree.append(item.tree())
                #print(ET.tostring(tree, encoding='unicode'))
        return tree