"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
import xml.etree.cElementTree as ET
from dataClass import _var,sectionAttribs

class Constants():
    def __init__(self,
                 T               : float = 0,
                 P               : float = 0,
                 R               : float = 8.31446,
                 Fc              : float = 96485.3,
                 attributes      : dict = {}):

        self.atr = sectionAttribs()
        self.atr.addAttrib(_var('T',T,attributes) )
        self.atr.addAttrib(_var('P',P,attributes) )
        self.atr.addAttrib(_var('R',R,attributes) )
        self.atr.addAttrib(_var('Fc',Fc,attributes) )

    def tree(self):
        tree = ET.Element('Constants')
        self.atr.fillTree(tree)
        return tree