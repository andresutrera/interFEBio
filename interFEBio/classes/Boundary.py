"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
from typing import Literal
from dataclasses import dataclass,fields
from typing import Optional,Union
import xml.etree.cElementTree as ET

# class Generic(object):


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


class fixedDisplacement():
    _dof = Literal['x','y','z']
    def __init__(self,name: str = None, nset: list|str|int = None, x_dof:int|str  = 0,y_dof:int|str  = 0,z_dof:int|str  = 0):
        
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
    def __init__(self,name: str = None, nset: list|str|int = None, dof: _dof = None,lc:str|int = 1, scale: float = 1.0, relative: bool = False, attributes: dict = {}):
        
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
        self.scale =    _var('scale',scale,attributes)
        self.relative = _var('relative',relative)

    def tree(self):
        tree = ET.Element('bc', name=self.name, node_set=self.nset.value, type='prescribed displacement')
        tree.append(self.dof.varTree())
        tree.append(self.scale.varTree())
        tree.append(self.relative.varTree())
        return tree
    
