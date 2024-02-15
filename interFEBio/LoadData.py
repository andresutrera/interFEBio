import xml.etree.cElementTree as ET
from typing import Literal
from .dataClass import _var,sectionAttribs

class loadController():
    def __init__(self,
                 id: str|int = 1,
                 name:str = 'LC1',
                 type: Literal['loadcurve'] = 'loadcurve',
                 interpolate: Literal['LINEAR'] = 'LINEAR',
                 extend: Literal['EXTRAPOLATE'] = 'EXTRAPOLATE',
                 points: list = [[0,0], [1,1]]):
        
        self.id = id
        self.name = name
        self.type = type

        self.interpolate = interpolate
        self.extend = extend
        self.points = points

    def tree(self):
        tree = ET.Element('load_controller', id=str(self.id), name=self.name, type=self.type)
        ET.SubElement(tree,'interpolate').text = self.interpolate
        ET.SubElement(tree,'extend').text = self.extend
        points = ET.SubElement(tree,'points')
        for point in self.points:
            ET.SubElement(points,'pt').text = '{},{}'.format(*point)

        return tree
    