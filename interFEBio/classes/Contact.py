"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
from typing import Literal
from dataclasses import dataclass,fields
from typing import Optional,Union
import xml.etree.cElementTree as ET
from dataClass import _var,sectionAttribs



class sliding_elastic():
    _opts = Literal[0,1]
    def __init__(self,
                 name                       : str = None,
                 surface_pair               : str = None,
                 laugon                     : int|str = 0,
                 tolerance                  : float|str = 0.2,              
                 gaptol                     : float|str = 0.0,
                 penalty                    : float|str = 1.0,
                 auto_penalty               : int|bool = False,
                 two_pass                   : int|bool = False,
                 search_tol                 : float|str = 0.01,
                 symmetric_stiffness        : int|str = 1,
                 search_radius              : float|str = 1.0,
                 seg_up                     : int|str = 0,
                 tension                    : int|bool = False,
                 minaug                     : int|str = 0.0,
                 maxaug                     : int|str = 10,
                 fric_coeff                 : float|str = 0.0,
                 smooth_aug                 : int|bool = False,
                 node_reloc                 : int|bool = False,
                 flip_primary               : int|bool = False,
                 flip_secondary             : int|bool = False,
                 knmult                     : float|str = 0.0,
                 update_penalty             : int|bool = False,
                 shell_bottom_primary       : int|bool = False,
                 shell_bottom_secondary     : int|bool = False,
                 attributes                 : dict = {}):
        
        self.type = 'sliding-elastic'
        self.name = name
        self.surface_pair = surface_pair
        
        self.atr = sectionAttribs()
        self.atr.addAttrib(_var('laugon',laugon,attributes) )
        self.atr.addAttrib(_var('tolerance',tolerance,attributes) )
        self.atr.addAttrib(_var('gaptol',gaptol,attributes) )
        self.atr.addAttrib(_var('penalty',penalty,attributes) )
        self.atr.addAttrib(_var('auto_penalty',auto_penalty,attributes) )
        self.atr.addAttrib(_var('two_pass',two_pass,attributes) )
        self.atr.addAttrib(_var('search_tol',search_tol,attributes) )
        self.atr.addAttrib(_var('symmetric_stiffness',symmetric_stiffness,attributes) )
        self.atr.addAttrib(_var('search_radius',search_radius,attributes) )
        self.atr.addAttrib(_var('seg_up',seg_up,attributes) )
        self.atr.addAttrib(_var('tension',tension,attributes) )
        self.atr.addAttrib(_var('minaug',minaug,attributes) )
        self.atr.addAttrib(_var('maxaug',maxaug,attributes) )
        self.atr.addAttrib(_var('fric_coeff',fric_coeff,attributes) )
        self.atr.addAttrib(_var('smooth_aug',smooth_aug,attributes) )
        self.atr.addAttrib(_var('node_reloc',node_reloc,attributes) )
        self.atr.addAttrib(_var('flip_primary',flip_primary,attributes) )
        self.atr.addAttrib(_var('flip_secondary',flip_secondary,attributes) )
        self.atr.addAttrib(_var('knmult',knmult,attributes) )
        self.atr.addAttrib(_var('update_penalty',update_penalty,attributes) )
        self.atr.addAttrib(_var('shell_bottom_primary',shell_bottom_primary,attributes) )
        self.atr.addAttrib(_var('shell_bottom_secondary',shell_bottom_secondary,attributes) )


    def tree(self):
        tree = ET.Element('contact', type=self.type, name=self.name, surface_pair=self.surface_pair)
        self.atr.fillTree(tree)
        return tree