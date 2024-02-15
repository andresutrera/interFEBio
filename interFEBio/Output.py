import xml.etree.cElementTree as ET
from typing import Literal
from .dataClass import _var,sectionAttribs

    

class plotVar():
    def __init__(self,name:str = None):
        self.name = name

    def tree(self):
        tree = ET.Element('var', type=self.name)
        return tree
    