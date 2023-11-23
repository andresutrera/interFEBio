import xml.etree.cElementTree as ET
from typing import Literal


    

class plotVar():
    def __init__(self,name:str = None):
        self.name = name

    def tree(self):
        tree = ET.Element('var', name=self.name)
        return tree
    