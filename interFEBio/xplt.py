"""
Module to read xply binary data resulting from a FEBio analysis.
Is based on the binary database Documentation and some recent source code (storage formats):

[FEBioBinaryDatabaseSpecification.pdf](https://github.com/febiosoftware/FEBio/blob/master/Documentation/FEBioBinaryDatabaseSpecification.pdf)

[fecore_enum](https://github.com/febiosoftware/FEBio/blob/f9a3cdd74d1864ec0886decc918ef8e805344fbc/FECore/fecore_enum.h)
"""

from .Enums import *
import struct
import numpy as np
from numpy import *
import sys
import pdb
import warnings
from typing import Dict

            
class data:
    def __init__(self, name: str = None, format:Storage_Fmt = Storage_Fmt.FMT_NODE, dataType:FEDataType = FEDataType.VEC3F):
        self.format = format
        self.dataType = dataType
        self.name = name

        self.data = [[]]#domain, time, node/item/region, axis
        self.dataTime = []

    def addData(self,domain: int = 0, data: list = None, time: float = None):
        if( domain+1 > len(self.data)):
             self.data.append([])#Append another domain list

        self.data[domain].append(data)

        if(time not in self.dataTime):
            self.dataTime.append(time)
    

    def toNumpy(self):
        self.data = [np.array(dom) for dom in self.data]

    def getData(self, domain: int = 0) -> np.ndarray:
        if( domain+1 > len(self.data) ):
            raise Exception("Domain integer is out of range ({} domains in file)".format(len(self.data)))
        return self.data[domain]
    
    def getDataTime(self):
        return np.array(self.dataTime)



class xplt:
    """
    Class that reads a binary file of FEBio.

    Args:
    ----------

        filename(str): Name of the xplt binary with extension.

    Variables:
    ----------

        self.dictionary :   A dictionary containing the results dictionary in the xplt file.
                            Resume the result variables and type of data for each one.

        self.results:       Numpy array of results in the following format:
                            self.results[time step, region, element/node/surface, component (voigt, starting from 0)]
    """
    def __init__(self,filename):
        self.rigidDictionary = dict()
        self.time = []
        self.reader = _binaryReader(filename)
        self.readMode = ''
        self._read_xplt(filename)



    def _readMesh(self):
        #self.mesh: mesh
        self.mesh = mesh() #Initialize mesh object.

        self.reader.search_block('PLT_MESH')
        self.reader.search_block('PLT_NODE_SECTION')
        self.reader.search_block('PLT_NODE_HEADER')
        self.reader.search_block('PLT_NODE_SIZE')
        nodeSize = (int(struct.unpack('I', self.reader.read())[0]))
        self.reader.search_block('PLT_NODE_DIM')
        nodeDim = (int(struct.unpack('I', self.reader.read())[0]))
        self.reader.search_block('PLT_NODE_COORDS')
        node_coords = zeros([nodeSize, nodeDim])
        #node_coords = zeros([1, nodeDim])
        for i in range(nodeSize):
            id = struct.unpack('I', self.reader.read())[0] #Is necessary to store this?
            #print(id)
            for j in range(nodeDim):
                node_coords[i, j] = struct.unpack('f', self.reader.read())[0]
        self.mesh.nodes = node_coords

        a = self.reader.search_block('PLT_DOMAIN_SECTION')

        # NOTE: index starts from 0 (in .feb file, index starts from 1)
        idomain = 1
        while self.reader.check_block('PLT_DOMAIN'):
            self.reader.search_block('PLT_DOMAIN')
            self.reader.search_block('PLT_DOMAIN_HDR')
            self.reader.search_block('PLT_DOM_ELEM_TYPE')
            dom_elem_type = int(struct.unpack('I', self.reader.read())[0])

            self.reader.search_block('PLT_DOM_PART_ID')
            dom_part_id = (int(struct.unpack('I', self.reader.read())[0]))

            self.reader.search_block('PLT_DOM_ELEMS')
            dom_n_elems = (int(struct.unpack('I', self.reader.read())[0]))
            isDomName = self.reader.search_block('PLT_DOM_NAME')

            if(isDomName > 0):
                dom_names = (self.reader.read(isDomName).decode("utf-8",errors="ignore"))
            else:
                dom_names = None
            elemDict = dict()

            self.reader.search_block('PLT_DOM_ELEM_LIST')

            etype = Elem_Type(dom_elem_type).name
            ne = nodesPerElementClass[etype]
            #print("ELEMSSSSSSSSS:",ne)
  
            while self.reader.check_block('PLT_ELEMENT'):
                a = self.reader.search_block('PLT_ELEMENT', print_tag=0)
                element = zeros(ne + 1, dtype=int)
                for j in range(ne + 1):
                    element[j] = struct.unpack('I', self.reader.read())[0]
                elemDict[element[0]-1] = element[1:]

            self.mesh.domain[dom_part_id-1] = domainClass(name = dom_names, elemType = Elem_Type(dom_elem_type).name, domainID=dom_part_id-1, nElems = dom_n_elems, elements=elemDict)
            idomain+=1


        if self.reader.search_block('PLT_SURFACE_SECTION') > 0:
            surface_ids = []
            surface_faces = []  # number of faces
            surface_names = []
            faces = []
            face_ids = []
            face_max_facet_nodes = []
            while self.reader.check_block('PLT_SURFACE'):
                a = self.reader.search_block('PLT_SURFACE')

                a = self.reader.search_block('PLT_SURFACE_HDR')

                a = self.reader.search_block('PLT_SURFACE_ID')
                surface_ids = (struct.unpack('I', self.reader.read())[0])

                # number of facets
                a = self.reader.search_block('PLT_SURFACE_FACES')
                surface_faces = (struct.unpack('I', self.reader.read())[0])

                a = self.reader.seek_block('PLT_SURFACE_NAME')
                # surface name length is specified just above
                surface_names = (self.reader.read(a).decode("utf-8",errors="ignore").split('\x00')[-1])

                a = self.reader.search_block('PLT_SURFACE_MAX_FACET_NODES')
                face_max_facet_nodes = (struct.unpack('I', self.reader.read())[0])
                if (self.reader.check_block('PLT_FACE_LIST') == 0):
                    continue
                else:
                    a = self.reader.search_block('PLT_FACE_LIST')
                facesDict = dict()
                while self.reader.check_block('PLT_FACE'):
                    a = self.reader.search_block('PLT_FACE')
                    cur_cur = self.reader.file.tell()

                    face = zeros(face_max_facet_nodes, dtype=int)
                    face_ids = (struct.unpack('I', self.reader.read())[0])

                    # skip (probably specifing the surface element type here)
                    self.reader.file.seek(4, 1)
                    # tri3 element

                    for j in range(face_max_facet_nodes):
                        face[j] = struct.unpack('I', self.reader.read())[0]
                    facesDict[face_ids] = face
                    #faces = (face)
                    # skip junk
                    self.reader.file.seek(cur_cur + a, 0)
                # self.mesh.surface[surface_ids] = {'name' : surface_names,
                #                                     'nFaces' : surface_faces,
                #                                     'nNodesPerFacet' : face_max_facet_nodes,
                #                                     'faces' : facesDict
                #                                     }
                self.mesh.surface[surface_ids-1] = surfaceClass(name = surface_names, nSurf=surface_faces, nNodesPerFacet=face_max_facet_nodes, faces=facesDict)
                #print(surface_names)


        if self.reader.search_block('PLT_NODESET_SECTION') > 0:

            nodeset_ids = []
            nodeset_nodes = []  # number of faces
            nodeset_names = []
            nodeset = []
            #face_ids = []
            while self.reader.check_block('PLT_NODESET'):
                a = self.reader.search_block('PLT_NODESET')

                a = self.reader.search_block('PLT_NODESET_HDR')

                a = self.reader.search_block('PLT_NODESET_ID')
                nodeset_ids = (struct.unpack('I', self.reader.read())[0])
                # number of facets
                a = self.reader.search_block('PLT_NODESET_SIZE')
                nodeset_nodes = (struct.unpack('I', self.reader.read())[0])
                a = self.reader.search_block('PLT_NODESET_NAME')
                # surface name length is specified just above
                nodeset_names = (self.reader.read(a).decode("utf-8",errors="ignore").split('\x00')[-1])

                if (self.reader.check_block('PLT_NODESET_LIST') == 0):
                    continue
                else:
                    a = self.reader.search_block('PLT_NODESET_LIST')
                    nodes = []
                    for j in range(nodeset_nodes):
                        nodes.append(struct.unpack('I', self.reader.read())[0])
                # self.mesh.nodeset[nodeset_ids] = {
                #                                     'name' : nodeset_names,
                #                                     'nodeNumber' : nodeset_nodes,
                #                                     'nodes' : nodes
                #                                     }
                #print(nodeset_ids)
                self.mesh.nodeset[nodeset_ids-1] = nodesetClass(name=nodeset_names, nNodes=nodeset_nodes, nodes=nodes)

    def _readParts(self):
        a = self.reader.search_block('PLT_PARTS_SECTION')
        while self.reader.check_block('PLT_PART'):
            a = self.reader.search_block('PLT_PART')
            a = self.reader.search_block('PLT_PART_ID')
            partID = (struct.unpack('I', self.reader.read())[0])
            a = self.reader.search_block('PLT_PART_NAME')
            partName = (self.reader.read(a).decode("utf-8",errors="ignore").split('\x00')[0])
            self.mesh.parts[partName] = partClass(name=partName, ID=partID)

        #print(self.mesh.parts)

    def _readDictStream(self, dictType):
        a = self.reader.search_block(dictType)
        while self.reader.check_block('PLT_DIC_ITEM'):
            a = self.reader.search_block('PLT_DIC_ITEM')
            a = self.reader.search_block('PLT_DIC_ITEM_TYPE')
            item_types = (int(struct.unpack('I', self.reader.read())[0]))
            a = self.reader.search_block('PLT_DIC_ITEM_FMT')
            item_formats = (int(struct.unpack('I', self.reader.read())[0]))
            a = self.reader.search_block('PLT_DIC_ITEM_NAME')
            item_names = (self.reader.read(64).decode("utf-8",errors="ignore").split('\x00')[0])
            self.dictionary[item_names] = {'type' : FEDataType(item_types).name, 'format' : Storage_Fmt(item_formats).name}


    def _readDict(self):

        self.dictionary = dict()

        self.reader.search_block('PLT_DICTIONARY')

        ############### NODAL DICTIONARY ###################
        self._readDictStream('PLT_DIC_NODAL')
        self._readDictStream('PLT_DIC_DOMAIN')
        self._readDictStream('PLT_DIC_SURFACE')




        self.results = dict()

        for key in self.dictionary.keys():
            self.results[key] = data(name=key)

        self.dictNodal = (sum(np.fromiter((1 for v in self.dictionary.values() if v['format'] == 'NODE') ,dtype=int)))
        self.dictItem = (sum(np.fromiter((1 for v in self.dictionary.values() if v['format'] == 'ITEM') ,dtype=int)))



    def _readObjState(self):
        a = self.reader.search_block('PLT_OBJECTS_SECTION')
        a = self.reader.search_block('PLT_POINT_OBJECT')
        a = self.reader.search_block('PLT_OBJECT_ID')
        objID = struct.unpack('I', self.reader.read())[0]

        #
        a = self.reader.search_block('PLT_OBJECT_NAME')
        #print(a)
        objName = (self.reader.read(a).decode("utf-8",errors="ignore").split("\x00")[-1])

        a = self.reader.search_block('PLT_OBJECT_TAG')
        objTAG = struct.unpack('I', self.reader.read())[0]

        a = self.reader.search_block('PLT_OBJECT_POS')
        objPOSX = struct.unpack('f', self.reader.read())[0]
        objPOSY = struct.unpack('f', self.reader.read())[0]
        objPOSZ = struct.unpack('f', self.reader.read())[0]


        a = self.reader.search_block('PLT_OBJECT_ROT')
        objROTX = struct.unpack('f', self.reader.read())[0]
        objROTY = struct.unpack('f', self.reader.read())[0]
        objROTZ = struct.unpack('f', self.reader.read())[0]
        objROTW = struct.unpack('f', self.reader.read())[0]

        self.reader.search_block('PLT_OBJECT_DATA')
        self.reader.search_block('PLT_DIC_ITEM_TYPE')
        itemType = struct.unpack('I', self.reader.read())[0]
        self.reader.search_block('PLT_DIC_ITEM_FMT')
        itemFmt = struct.unpack('I', self.reader.read())[0]

        self.rigidDictionary[objID] = { 'name' : objName,
                                        'tag' : objTAG,
                                        'pos' : [objPOSX,objPOSY,objPOSZ],
                                        'rot' : [objROTX,objROTY,objROTZ,objROTW],
                                        'itemType' : FEDataType(itemType).name,
                                        'itemFmt' : itemFmt
                                    }

    def _skipState(self):
        a = self.reader.seek_block('PLT_STATE')
        self.reader.read(a)

    def readSteps(self,stepList):
        """
        Read a list of time steps.

        Variables:
        ----------

            stepList(list): List of integers. Time steps to be read.

        TODO:
        ----------

            Fix this function. The last step of the list can't be readed.

        """
        if(self.readMode == 'readAllStates'):
            sys.exit("readSteps[list] is not compatible with readAllStates function")

        for i in range(len(stepList)):
            if(i == 0):
                stepDiff = stepList[i]
            else:
                stepDiff = stepList[i] - stepList[i-1]
            #print(stepDiff)
            if(i>0):
                stepDiff-=1

            for skip in range(stepDiff):
                try:
                    self._skipState()
                except:
                    sys.exit("*******************************\n\n"+"Error: No more steps to skip!!!\n\n"+"*******************************")
            self._readState()
        self.readMode = 'readSteps'
            #try:
            #    self.skipState()
            #except:
            #    sys.error("No more states to skip")
        #self.readState()
        self._clearDict()
        self.reader.file.close()


    def _readResultStream(self,dataType):
        a = self.reader.search_block(dataType)
        while self.reader.check_block('PLT_STATE_VARIABLE'):
            self.reader.search_block('PLT_STATE_VARIABLE')
            self.reader.search_block('PLT_STATE_VAR_ID')
            varID = struct.unpack('I', self.reader.read())[0]

            dataLength = self.reader.search_block('PLT_STATE_VAR_DATA')

            a_end = self.reader.file.tell() + dataLength

            #dictKey = list(self.dictionary.keys())[varID-1]
            dictKey = list(self.dictionary.keys())[self.var]
            dataDim = (FEDataDim[self.dictionary[dictKey]['type']].value)

           # self.results[dictKey].addDataTime(self.time[-1])
            while(self.reader.file.tell() < a_end):
                dom_num = struct.unpack('I', self.reader.read())[0]
                if(dictKey != 'displacement'): dom_num-=1
                data_size = struct.unpack('I', self.reader.read())[0]
                n_data = int(data_size / dataDim / 4.0)

                if n_data > 0:
                    elem_data = zeros([n_data, dataDim])
                    for i in range(0, n_data):
                        for j in range(0, dataDim):
                            elem_data[i, j] = struct.unpack('f', self.reader.read())[0]

                self.results[dictKey].addData(dom_num,elem_data,self.time[-1])

            self.var+=1

        


    def _readState(self):

        self.var = 0


        # # now extract the information from the desired state
        self.reader.search_block('PLT_STATE')
        self.reader.search_block('PLT_STATE_HEADER')
        # a = self.reader.search_block('PLT_STATE_HDR_ID')
        # stateID = struct.unpack('I', self.reader.read())[0]
        # print(stateID)

        self.reader.search_block('PLT_STATE_HDR_TIME')
        stateTime = struct.unpack('f', self.reader.read())[0]


        self.reader.search_block('PLT_STATE_STATUS')
        stateStatus = struct.unpack('I', self.reader.read())[0] #What is state status?
        #print("STATSTATUS",stateStatus)
        if(stateStatus != 0):
            return 1
        self.time.append(stateTime)

        self.reader.search_block('PLT_STATE_DATA')

        try:
            self._readResultStream('PLT_NODE_DATA')
            self._readResultStream('PLT_ELEMENT_DATA')
            self._readResultStream('PLT_FACE_DATA')
        except Exception as e:
            pass
            #print(e)
            



        return 0


    def readAllStates(self):
        """
        Read all the steps of the xplt file.
        """
        if(self.readMode) == 'readSteps':
            sys.exit("readAllStates is not compatible with readSteps[list]!")
        i=1
        while (1):
            try:
                #print(i)

                status = self._readState()
                #print(i,status)
                i+=1
                if(status != 0):
                    break
            except Exception as e:
                #print(e)
                break
        self.readMode = 'readAllStates'
        self._clearDict()

    def _clearDict(self):
        for key in self.results:
            self.results[key].toNumpy()


    def _read_xplt(self,filename):
        FEBioFile = struct.unpack('I', self.reader.read())[0]
        if(4605250 != FEBioFile):
            sys.exit("The provided file is not a valid xplt file")
        self.reader.search_block('PLT_ROOT')
        self.reader.search_block('PLT_HEADER')
        self.reader.search_block('PLT_HDR_VERSION')
        self.version = struct.unpack('I', self.reader.read())[0]

        self.reader.search_block('PLT_HDR_COMPRESSION')
        self.compression = struct.unpack('I', self.reader.read())[0]
        self._readDict()
        self._readMesh()
        self._readParts()

class _binaryReader:
    def __init__(self,filename):

        self.file = open(filename, 'rb')
        self.file.seek(0, 2)
        self.filesize = self.file.tell() #Get file size
        self.file.seek(0, 0)

    def read(self,bytes=4):
        return self.file.read(bytes)

    def search_block(self, BLOCK_TAG, max_depth=5, cur_depth=0,verbose=0, inv_TAGS=0, print_tag=0):

        if cur_depth == 0:
            ini_pos = self.file.tell()
        if cur_depth > max_depth:
            if verbose == 1:
                print('Max iteration reached: Cannot find ',BLOCK_TAG)
            return -1
        buf = self.file.read(4)
        if buf == b'':
            if verbose == 1:
                print('EOF: Cannot find ',BLOCK_TAG)
            return -1
        else:
            cur_id = struct.unpack('I', buf)[0]
        a = struct.unpack('I', self.file.read(4))[0]  # size of the block
        if verbose == 1:
            cur_id_str = '0x' + '{0:08x}'.format(cur_id)
            # print 'cur_ID: ' + cur_id_str
            try:
                print('cur_tag:', tags(cur_id_str).name)
                #print('size:', a)
            except Exception as e:
                print(e)
        #print(tags[BLOCK_TAG])
        if(int(tags[BLOCK_TAG].value, base=16) == cur_id):
            if print_tag == 1:
                print(BLOCK_TAG)
            return a
        else:
            self.file.seek(a, 1)
            d = self.search_block(BLOCK_TAG, cur_depth=cur_depth + 1,verbose=verbose,print_tag=print_tag)
            if d == -1:
                # put the cursor position back
                if cur_depth == 0:
                    self.file.seek(ini_pos, 0)
                return -1
            else:
                return d

    def check_block(self,BLOCK_TAG, filesize=-1):
        '''Check if the BLOCK TAG exists immediately after the file cursor.'''
        if filesize > 0:
            if self.file.tell() + 4 > filesize:
                print("EOF reached")
                return 0
        buf = struct.unpack('I', self.file.read(4))[0]
        self.file.seek(-4, 1)
        if(int(tags[BLOCK_TAG].value, base=16) == buf):
            return 1
        return 0

    def seek_block(self,BLOCK_TAG):
        if(int(tags[BLOCK_TAG].value, base=16) == struct.unpack('I', self.file.read(4))[0]):
            pass
            #print('%s' % BLOCK_TAG)
        a = struct.unpack('I', self.file.read(4))  # size of the root section
        return a[0]



class domainClass:
    def __init__(self, name:str = None, elemType: str = None, domainID: int = None, nElems: int = None, elements: dict = None):
        self.name = name
        self.elemType = elemType
        self.domainID = domainID
        self.nElems = nElems
        self.elements = elements
    def __repr__(self) -> str:
        return(str(self.name))
    
class nodesetClass:
    def __init__(self, name:str = None, nNodes: int = None, nodes: dict = None):
        self.name = name
        self.nNodes = nNodes
        self.nodes = nodes

    def __repr__(self) -> str:
        return(str(self.name))

class surfaceClass:
    def __init__(self, name:str = None, nSurf: int = None, nNodesPerFacet:int = None, faces: dict = None):
        self.name = name
        self.nSurf = nSurf
        self.nNodesPerFacet = nNodesPerFacet
        self.faces = faces
    def __repr__(self) -> str:
        return(str(self.name))
    
class partClass:
    def __init__(self, name:str = None, ID: int = None):
        self.name = name
        self.ID = ID
    def __repr__(self) -> str:
        return(str(self.ID))

class mesh():
    """
    Child class inside the xplt main class that allows to access information of the mesh.

    Variables:
    ----------

        self.domain (dict): Dictionary of domains. the key is the domain ID.
                            Contains another dictionary with the following keys:
                                'elemType'  : (str)  Type of element
                                'partID'    : (int)  Part id (same as domain ID, should be removed)
                                'nElems'    : (int)  Number of elements in that domain
                                'elements'  : (dict) Dictionary of elements. The keys are the element number.

        self.nodeset (dict): Dictionary of nodesets. the key is the nodeset ID.
                             Contains another dictionary with the following keys:
                                'name'       : (str)  Name of that nodeset
                                'nodeNumber' : (int)  Number of nodes of the nodeset
                                'nodes'      : (list) List of nodes

        self.surface (dict): Dictionary of surfaces. the key is the surface ID.
                             Contains another dictionary with the following keys:
                                'name'           : (str)  Surface name
                                'nFaces'         : (int)  Surface number of facets
                                'nNodesPerFacet' : (int)  Surface nodes per facet
                                'faces'          : (dict) Dictionary of faces elements.
                                                          The key is the facet element number.
                                                          Contain a list of nodes for each facet (size nNodesPerFacet).

    """
    def __init__(self):
        self.domain: Dict[int,domainClass] = dict()
        self.nodeset: Dict[int,nodesetClass] = dict()
        self.surface: Dict[int,surfaceClass] = dict()
        self.parts: Dict[str,partClass] = dict()

    
    def listRegions(self) -> list:
        """
        List all the regions of the mesh

        Return:
        ----------
                List of region names
        """
        return [x for x in self.parts.keys()]

    def listSurfaces(self):
        """
        List all the surface names of the mesh

        Return:
        ----------
                List of surface names
        """
        return [self.surface[x].name for x in self.surface.keys()]

    def listNodesets(self):
        """
        List all the nodeset names of the mesh

        Return:
        ----------
                List of nodeset names
        """
        return [self.nodeset[x].name for x in self.nodeset.keys()]

    def regionID(self,name):
        """
        Return the integer ID of a region by its name

        Variables:
        ----------

            name(str): Name of the region

        Return:
        ----------
        regionID (int)

        """
        return self.parts[name].ID

    def surfaceID(self,name):
        """
        Return the integer ID of a surface by its name

        Variables:
        ----------

            name(str): Name of the surface

        Return:
        ----------

            surface ID (int)
        """
        for key in self.surface.keys():
            if(self.surface[key].name == name):
                return key

    def nodesetID(self,name:str = None) -> str:
        """
        Return the integer ID of a nodeset by its name

        Variables:
        ----------

            name(str): Name of the nodeset

        Return:
        ----------

            nodeset ID (int)
        """
        if(name is None):
            raise Exception("Name cant be empty")
        for key in self.nodeset.keys():
            if(self.nodeset[key].name == name):
                return key

    def domainElements(self,domain):
        """
        Return the elements of a given domain ID.

        Variables:
        ----------

            domain(int): Name of the region

        Return:
        ----------

            dictionary of elements in that domain.
        """
        return self.domain[domain].elements

    # def allElements(self):
    #     """
    #     Return a dictionary of all the elements of the mesh.

    #     Return:
    #     ----------

    #         dictionary of all the elements of the mesh.
    #     """
    #     totalElementDict = dict()
    #     for key in self.domain.keys():
    #         for elem in self.domain[key]['elements']:
    #             totalElementDict[elem] = self.domain[key]['elements'][elem]
    #     return totalElementDict
    def __repr__(self) -> str:
        return("Domains:\t{}\nNodesets:\t{}\nSurfaces:\t{}\nParts:\t\t{}".format(self.domain,self.nodeset,self.surface,self.parts))
    
    
