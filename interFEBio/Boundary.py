"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
from typing import Literal
from typing import Optional,Union
import xml.etree.cElementTree as ET
from .dataClass import _var,sectionAttribs

class fixedDisplacement():
    _dof = Literal['x','y','z']
    def __init__(self,
                 name       : str = None,
                 nset       : list|str|int = None,
                 x_dof      : int|str  = 0,
                 y_dof      : int|str  = 0,
                 z_dof      : int|str  = 0):
        
        self.name = name
        if isinstance(nset, list):
            #pass #Add nodeset to mesh definition
            self.nset = _var('node_set',nset)
            print("LIST TO NODESET NOT IMPLEMENTED")
        elif isinstance(nset, str):
            self.nset = _var('node_set',nset)
        elif isinstance(nset, int):
            self.nset = _var('node',nset)

        self.x_dof = _var('x_dof',x_dof)
        self.y_dof = _var('y_dof',y_dof)
        self.z_dof = _var('z_dof',z_dof)


    def tree(self):
        tree = ET.Element('bc', name=self.name, node_set=self.nset.value, type='zero displacement')
        tree.append(self.x_dof.varTree())
        tree.append(self.y_dof.varTree())
        tree.append(self.z_dof.varTree())
        return tree
    

class prescribedDisplacement():
    _dof = Literal['x','y','z']
    def __init__(self,name: str = None, nset: list|str|int = None, dof: _dof = None,lc:str|int = 1, value: float = 1.0, relative: int = 0, attributes: dict = {}):
        
        self.name = name
        self.lc = lc
        if isinstance(nset, list):
            #pass #Add nodeset to mesh definition
            self.nset = _var('node_set',nset)
            print("LIST TO NODESET NOT IMPLEMENTED")
        elif isinstance(nset, str):
            self.nset = _var('node_set',nset)
        elif isinstance(nset, int):
            self.nset = _var('node',nset)

        self.dof =      _var('dof',dof)
        self.value =    _var('value',value,attributes)
        self.relative = _var('relative',relative)

    def tree(self):
        tree = ET.Element('bc', name=self.name, node_set=self.nset.value, type='prescribed displacement')
        tree.append(self.dof.varTree())
        tree.append(self.value.varTree())
        tree.append(self.relative.varTree())
        return tree
    
