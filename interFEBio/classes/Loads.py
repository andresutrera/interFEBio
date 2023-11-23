"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
from typing import Literal
from dataclasses import dataclass,fields
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


class surface_load():
    _opts = Literal[0,1]
    def __init__(self,name: str = None, surface: str = None,type:str = 'pressure', pressure:str|float = 0.0, symmetric_stiffness:_opts = 1, linear:_opts = 0, shell_bottom:_opts = 0,attributes: dict = {}):
        
        self.name = name
        self.surface = surface
        self.type = type
        self.pressure =_var('pressure',pressure,attributes)
        self.symmetric_stiffness =_var('symmetric_stiffness',symmetric_stiffness,attributes)
        self.linear =_var('linear',linear,attributes)
        self.shell_bottom =_var('shell_bottom',shell_bottom,attributes)

    def tree(self):
        tree = ET.Element('surface_load', name=self.name, surface=self.surface, type=self.type)
        tree.append(self.pressure.varTree())
        tree.append(self.symmetric_stiffness.varTree())
        tree.append(self.linear.varTree())
        tree.append(self.shell_bottom.varTree())
        return tree
    
