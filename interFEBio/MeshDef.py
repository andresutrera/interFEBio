"""
This class handles the mesh data.

a interface between a mesh file (just gmsh for now) is used to get the
mesh nodes, elements, nodesets, surfaces and element sets for making the .feb file.

# TODO

 - Add more mesh interfaces. Just gmsh is implemented.
 - Check for gmsh second order elements.

"""
from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import map
from builtins import range
from builtins import object
from past.utils import old_div
import numpy as np
import sys

class MeshDef(object):
    '''
    Class to store element, node, and set definitions

    Can parse just gmsh files (2.0 and 2.2 formats for now).

    Args:
    ----------

        mfile(str):             Mesh file.

        mformat(str):           Mesh format. (gmsh)

        scale(list):            List of scale for nodal positions. default = [1.0, 1.0, 1.0]

        physicalEntities(list): List of strings. physical entities to be added to the mesh.
                                The remaining entities defined in the mesh file will be added as surfaces
                                and nodesets.

        print(dict):            Dictionary to print the readed mesh data in the format 'key':True/False.
                                The supported keys are 'nodes','elements','elsets','fsets','nsets'.

    '''


    def __init__(self,mfile=None,mformat='manual',scale=[1.0,1.0,1.0],physicalEntities=None,print={'nodes':False,'elements':False,'elsets':False,'fsets':False, 'nsets':False}):
        self.mfile = mfile
        self.mformat = mformat
        #elements[element] = {'type' : elementType, 'nodes' : [listOfNodes]}
        self.elements = dict()
        #nodes[node] = {[x, y, z]}
        self.nodes = dict()
        self.scale = list(map(float,scale))
        #elsets[set] = {'elements' : [listOfElements], 'type' : elementType}
        self.elsets = dict()
        #nsets[set] = {'nodes' : [listOfNodes]}
        self.nsets = dict()
        #fsets[set] = {'elements' : [[elem1],[elem2],[elem3],....], 'type' : elemType}
        self.fsets = dict()

        self.print = print

        self.physicalEntities = physicalEntities

        self.facetID = 1 #counter to assign unique IDs to surface facets defined in sets

        #Mapping from the gmsh element to the resulting element for FEBio.
        #This class will ignore the physical surfaces/lines/nodes as elements, but they will be
        #included in fsets and nsets
        self.elementMapping = dict()

        #print(physicalEntities)

        self.elementData = []
        if self.mfile is not None:
            self._parseMesh()

    def _parseMesh(self):
        if self.mformat.lower() == 'gmsh':
            supportedFormats = ['2.2', '2.0']

            with open(self.mfile) as f:
                lines = [line.strip() for line in f]

            mshFormat = lines[lines.index('$MeshFormat')+1].split()[0]
            if(mshFormat not in supportedFormats):
                sys.exit("Error: Gmsh version {} not supported".format(mshFormat))

            nodeLines = [lines.index('$Nodes')+2, lines.index('$EndNodes')-1]
            elemLines = [lines.index('$Elements')+2, lines.index('$EndElements')-1]
            physicalNamesLines = [lines.index('$PhysicalNames')+2, lines.index('$EndPhysicalNames')-1]
            physicalNames = dict()
            for i in lines[physicalNamesLines[0]:physicalNamesLines[1]+1]:
                dim = int(i.split()[0])
                dimName = {0: 'node',1: 'line', 2:'surface', 3:'volume'}
                id = int(i.split()[1])
                name = (i.split()[2].split('"')[1])
                physicalNames[id] = {'name':name, 'type':dimName[dim]}

                if((dimName[dim] == 'volume' or dimName[dim] == 'surface') and name in self.physicalEntities):
                    self.elsets[str(name)] = {}
                    self.elsets[str(name)]['elements'] = []
                if(dimName[dim] == 'surface'):
                    self.fsets[str(name)] = {}
                    self.fsets[str(name)]['elements'] = []
                    self.nsets[str(name)] = {}
                    self.nsets[str(name)]['nodes'] = []



            for i in lines[nodeLines[0]:nodeLines[1]+1]:
                nodeList = i.split()
                self.nodes[int(nodeList[0])] =self.__scaleNode(list(map(float,nodeList[1:])))


            for i in lines[elemLines[0]:elemLines[1]+1]:
                etypeNum = i.split()[1]
                elemNum = i.split()[0]
                elemList = i.split()[5:]
                physicalID = int(i.split()[3])
                if(etypeNum == '3'):
                    etype = 'quad4'
                elif(etypeNum == '4'):
                    etype = 'tet4'
                elif(etypeNum == '5'):
                    etype = 'hex8'
                elif(etypeNum == '6'):
                    etype = 'penta6'
                elif(etypeNum == '2'):
                    etype = 'tri3'
                else:
                    print("Error: Gmsh element type number {} not supported. skipping".format(int(etypeNum)))
                    continue

                if(physicalID in physicalNames):
                    setname = physicalNames[physicalID]['name']
                    isVolume = physicalNames[physicalID]['type'] == 'volume'
                    isSurface = physicalNames[physicalID]['type'] == 'surface'
                    isPhysical = physicalNames[physicalID]['name'] in self.physicalEntities
                    if((isVolume or isSurface) and isPhysical):
                        self.elementMapping[elemNum] = len(self.elements.keys())
                        elemDict = {}
                        elemDict['type'] = etype
                        elemDict['nodes'] = list(map(int,elemList))
                        self.elements[self.elementMapping[elemNum]] = elemDict

                        #Map the gmsh element number to the final element of the mesh
                        self.elsets[setname]['elements'].append(self.elementMapping[elemNum])
                        if(not "type" in self.elsets[setname]):
                            self.elsets[setname]['type'] = etype

                    if(physicalNames[physicalID]['type'] == 'surface'):
                        #dmy = [etype,MeshDef.facetID]
                        #print(dmy)
                        self.fsets[setname]['elements'].append(list(map(int,elemList)))
                        if(not "type" in self.fsets[setname]):
                            self.fsets[setname]['type'] = etype
                            #MeshDef.facetID += 1

                        for node in list(map(int,elemList)):
                            if not(node in self.nsets[setname]['nodes']):
                                self.nsets[setname]['nodes'].append(node)

            for key in self.print:
                if(key == 'nodes'):
                    if(self.print[key]):
                        print(self.nodes)
                if(key == 'elements'):
                    if(self.print[key]):
                        print(self.elements)
                if(key == 'elsets'):
                    if(self.print[key]):
                        print(self.elsets)
                if(key == 'fsets'):
                    if(self.print[key]):
                        print(self.fsets)
                if(key == 'nsets'):
                    if(self.print[key]):
                        print(self.nsets)

    def addElementSet(self,setname=None,eids=None,type=None):
        '''
        Add a element set manually.

        Args:
        ----------

            setname(str):  Name of the nodeset to be added.

            eids(list):    List of elements to be added in that element set.

            type(str):     Type of element (hex8, hex20, etc).
        '''
        if setname is None:
            print("WARNING: Must provide a setname. Skipping set generation...")
            pass
        if eids is None:
            print("WARNING: Did not specify any element IDs.  Skipping set generation...")
            pass
        if type is None:
            print("WARNING: Did not specify any element type.  Skipping set generation...")
            pass

        self.elsets[setname] = {}
        self.elsets[setname]['elements'] = []
        for element in eids:
            self.elsets[setname]['elements'].append(element)
        self.elsets[setname]['type'] = type

    def addNodeSet(self,setname=None,nids=None):
        '''
        Add a nodeset set manually.

        Args:
        ----------

            setname(str):  Name of the nodeset to be added.

            nids(list):    List of nodes to be added in that nodeset.
        '''
        if setname is None:
            print("WARNING: Must provide a setname. Skipping set generation...")
            pass
        if nids is None:
            print("WARNING: Did not specify any element IDs.  Skipping set generation...")
            pass

        self.nsets[setname] = {}
        self.nsets[setname]['nodes'] = []
        for node in nids:
            self.nsets[setname]['nodes'].append(node)

    def addSurfaceSet(self,setname=None,felems=None,type=None):
        '''
        Add a surface set manually.

        Args:
        ----------

            setname(str):   Name of the nodeset to be added.

            felems(list):   List of elements and nodes to be added in that surface set.
                            The list needs to be a list of list containing the nodes of each facet element:
                            e.g. [[1,2,3,4],[3,4,5,6]]

            type(str):     Type of element (quad4, tri3).

        '''
        if setname is None:
            print("WARNING: Must provide a setname. Skipping set generation...")
            pass
        if fids is None:
            print("WARNING: Did not specify any element IDs.  Skipping set generation...")
            pass
        if type is None:
            print("WARNING: Did not specify any element type.  Skipping set generation...")
            pass
        self.fsets[setname] = {}
        self.fsets[setname]['elements'] = []
        for element in felems:
            self.fsets[setname]['elements'].append(element)
        self.fsets[setname]['type'] = type

    def __scaleNode(self,node):
        return [node[0]*self.scale[0],node[1]*self.scale[1],node[2]*self.scale[2]]

    def addElementData(self, attrubutes,tree):
        '''
        Add element data (material axes, prestrain, etc).

        Args:
        ----------

            attrubutes(dict):   Dictionary of attributes of the ElementData

            tree(ET):           Element Tree containing each element ElementData inside an arbitrary root tag.
        '''
        self.elementData.append({'attrubutes' : attrubutes, 'tree' : tree})
