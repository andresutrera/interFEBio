"""
xplt.py

Read FEBio xplt binary data

https://github.com/febiosoftware/FEBio/blob/master/Documentation/FEBioBinaryDatabaseSpecification.pdf

"""

import struct
import numpy as np
from numpy import *
import sys
import pdb

class binaryReader:
    def __init__(self,filename):

        self.tags = {
            'PLT_VERSION' : '0x0031',
            'PLT_ROOT' : '0x01000000' ,
            'PLT_HEADER' : '0x01010000' ,
            'PLT_HDR_VERSION' : '0x01010001' ,
            #//	PLT_HDR_NODES' : '0x01010002' ,
            #//	PLT_HDR_MAX_FACET_NODES' : '0x01010003' ,	#// removed (redefined in seach SURFACE section)
            'PLT_HDR_COMPRESSION' : '0x01010004' ,
            'PLT_HDR_AUTHOR' : '0x01010005' ,#	// new in 2.0
            'PLT_HDR_SOFTWARE' : '0x01010006' ,	#// new in 2.0
            'PLT_DICTIONARY' : '0x01020000' ,
            'PLT_DIC_ITEM' : '0x01020001' ,
            'PLT_DIC_ITEM_TYPE' : '0x01020002' ,
            'PLT_DIC_ITEM_FMT' : '0x01020003' ,
            'PLT_DIC_ITEM_NAME' : '0x01020004' ,
            'PLT_DIC_ITEM_ARRAYSIZE' : '0x01020005' ,	#// added in version 0x05
            'PLT_DIC_ITEM_ARRAYNAME' : '0x01020006' ,	#// added in version 0x05
            'PLT_DIC_GLOBAL' : '0x01021000' ,
            #//	PLT_DIC_MATERIAL	' : '0x01022000' ,#	// this was removed
            'PLT_DIC_NODAL' : '0x01023000' ,
            'PLT_DIC_DOMAIN' : '0x01024000' ,
            'PLT_DIC_SURFACE' : '0x01025000' ,
            #//PLT_MATERIALS	' : '0x01030000' ,	#	// This was removed
            #//	PLT_MATERIAL' : '0x01030001' ,
            ##//	PLT_MAT_ID	' : '0x01030002' ,
            #//	PLT_MAT_NAME' : '0x01030003' ,
            'PLT_MESH' : '0x01040000' ,	#	// this was PLT_GEOMETRY
            'PLT_NODE_SECTION' : '0x01041000' ,
            'PLT_NODE_HEADER' : '0x01041100' ,	#	// new in 2.0
            'PLT_NODE_SIZE' : '0x01041101' ,	#	// new in 2.0
            'PLT_NODE_DIM' : '0x01041102' ,	#	// new in 2.0
            'PLT_NODE_NAME' : '0x01041103' ,	#	// new in 2.0
            'PLT_NODE_COORDS' : '0x01041200' ,	#	// new in 2.0
            'PLT_DOMAIN_SECTION' : '0x01042000' ,
            'PLT_DOMAIN' : '0x01042100' ,
            'PLT_DOMAIN_HDR' : '0x01042101' ,
            'PLT_DOM_ELEM_TYPE' : '0x01042102' ,
            'PLT_DOM_PART_ID' : '0x01042103' ,#// this was PLT_DOM_MAT_ID
            'PLT_DOM_ELEMS' : '0x01032104' ,
            'PLT_DOM_NAME' : '0x01032105' ,
            'PLT_DOM_ELEM_LIST' : '0x01042200' ,
            'PLT_ELEMENT' : '0x01042201' ,
            'PLT_SURFACE_SECTION' : '0x01043000' ,
            'PLT_SURFACE' : '0x01043100' ,
            'PLT_SURFACE_HDR' : '0x01043101' ,
            'PLT_SURFACE_ID' : '0x01043102' ,
            'PLT_SURFACE_FACES' : '0x01043103' ,
            'PLT_SURFACE_NAME' : '0x01043104' ,
            'PLT_SURFACE_MAX_FACET_NODES' : '0x01043105' ,	#// new in 2.0 (max number of nodes per facet)
            'PLT_FACE_LIST' : '0x01043200' ,
            'PLT_FACE' : '0x01043201' ,
            'PLT_NODESET_SECTION' : '0x01044000' ,
            'PLT_NODESET' : '0x01044100' ,
            'PLT_NODESET_HDR' : '0x01044101' ,
            'PLT_NODESET_ID' : '0x01044102' ,
            'PLT_NODESET_NAME' : '0x01044103' ,
            'PLT_NODESET_SIZE' : '0x01044104' ,
            'PLT_NODESET_LIST' : '0x01044200' ,
            'PLT_PARTS_SECTION' : '0x01045000' ,#// new in 2.0
            'PLT_PART' : '0x01045100' ,
            'PLT_PART_ID' : '0x01045101' ,
            'PLT_PART_NAME' : '0x01045102' ,
            #	// plot objects were added in 3.0
            'PLT_OBJECTS_SECTION' : '0x01050000' ,
            'PLT_OBJECT_ID' : '0x01050001' ,
            'PLT_OBJECT_NAME' : '0x01050002' ,
            'PLT_OBJECT_TAG' : '0x01050003' ,
            'PLT_OBJECT_POS' : '0x01050004' ,
            'PLT_OBJECT_ROT' : '0x01050005' ,
            'PLT_OBJECT_DATA' : '0x01050006' ,
            'PLT_POINT_OBJECT' : '0x01051000' ,
            'PLT_POINT_COORD' : '0x01051001' ,
            'PLT_LINE_OBJECT' : '0x01052000' ,
            'PLT_LINE_COORDS' : '0x01052001' ,
            'PLT_STATE' : '0x02000000' ,
            'PLT_STATE_HEADER' : '0x02010000' ,
            'PLT_STATE_HDR_ID' : '0x02010001' ,
            'PLT_STATE_HDR_TIME' : '0x02010002' ,
            'PLT_STATE_STATUS' : '0x02010003' ,	#// new in 3.1
            'PLT_STATE_DATA' : '0x02020000' ,
            'PLT_STATE_VARIABLE' : '0x02020001' ,
            'PLT_STATE_VAR_ID' : '0x02020002' ,
            'PLT_STATE_VAR_DATA' : '0x02020003' ,
            'PLT_GLOBAL_DATA' : '0x02020100' ,
            #//PLT_MATERIAL_DATA' : '0x02020200' ,// this was removed
            'PLT_NODE_DATA' : '0x02020300' ,
            'PLT_ELEMENT_DATA' : '0x02020400' ,
            'PLT_FACE_DATA' : '0x02020500' ,
            'PLT_MESH_STATE' : '0x02030000' ,
            'PLT_ELEMENT_STATE' : '0x02030001' ,
            'PLT_OBJECTS_STATE' : '0x02040000'
            }

        self.invTags = {v: k for k, v in self.tags.items()}
        self.file = open(filename, 'rb')
        self.file.seek(0, 2)
        self.filesize = self.file.tell() #Get file size
        self.file.seek(0, 0)

    def read(self,bytes=4):
        return self.file.read(bytes)

    def search_block(self, BLOCK_TAG, max_depth=15, cur_depth=0,verbose=0, inv_TAGS=0, print_tag=0):

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
                print('cur_tag:', self.invTags[cur_id_str])
                #print('size:', a)
            except:
                pass
        if(int(self.tags[BLOCK_TAG], base=16) == cur_id):
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
        if(int(self.tags[BLOCK_TAG], base=16) == buf):
            return 1
        return 0

    def seek_block(self,BLOCK_TAG):
        if(int(self.tags[BLOCK_TAG], base=16) == struct.unpack('I', self.file.read(4))[0]):
            pass
            #print('%s' % BLOCK_TAG)
        a = struct.unpack('I', self.file.read(4))  # size of the root section
        return a[0]

class mesh:
    def __init__(self):
        self.domain = dict()
        self.nodeset = dict()
        self.parts = dict()
        self.surface = dict()

    def domainElements(self,domain):
        return self.domain[domain]['elements']

    def allElements(self):
        totalElementDict = dict()
        for key in self.domain.keys():
            for elem in self.domain[key]['elements']:
                totalElementDict[elem] = self.domain[key]['elements'][elem]
        return totalElementDict


class xplt:
    def __init__(self,filename):
        self.rigidDictionary = dict()
        self.time = []
        self.reader = binaryReader(filename)
        self.readMode = ''
        self.read_xplt(filename)

    def listRegions(self):
        return [x for x in self.mesh.parts.keys()]

    def listSurfaces(self):
        return [self.mesh.surface[x]['name'] for x in self.mesh.surface.keys()]

    def listNodesets(self):
        return [self.mesh.nodeset[x]['name'] for x in self.mesh.nodeset.keys()]

    def regionID(self,name):
        return self.mesh.parts[name]

    def surfaceID(self,name):
        for key in self.mesh.surface.keys():
            if(self.mesh.surface[key]['name'] == name):
                return key
    def nodesetID(self,name):
        for key in self.mesh.nodeset.keys():
            if(self.mesh.nodeset[key]['name'] == name):
                return key

    def readMesh(self):
        self.mesh = mesh() #Initialize mesh object.
        elemType = {
            0 : 'HEX8',
            1 : 'PENTA6',
            2 : 'TET4',
            3 : 'QUAD4',
            4 : 'TRI3',
            5 : 'TRUSS2',
            6 : 'HEX20',
            7 : 'TET10',
            8 : 'TET15',
            9 : 'HEX27'
            }

        nodesPerElement = {
            'HEX8'   : 8,
            'PENTA6' : 6,
            'TET4'   : 4,
            'QUAD4'  : 4,
            'TRI3'   : 3,
            'TRUSS2' : 2,
            'HEX20' :20,
            'TET10' : 10,
            'TET15' : 15,
            'HEX27' : 27
        }

        a = self.reader.search_block('PLT_MESH')
        a = self.reader.search_block('PLT_NODE_SECTION')
        a = self.reader.search_block('PLT_NODE_HEADER')
        a = self.reader.search_block('PLT_NODE_SIZE')
        nodeSize = (int(struct.unpack('I', self.reader.read())[0]))
        a = self.reader.search_block('PLT_NODE_DIM')
        nodeDim = (int(struct.unpack('I', self.reader.read())[0]))
        a = self.reader.search_block('PLT_NODE_COORDS')
        node_coords = zeros([nodeSize, nodeDim])
        #node_coords = zeros([1, nodeDim])
        for i in range(nodeSize):
            id = struct.unpack('I', self.reader.read())[0] #Is necessary to store this?
            for j in range(nodeDim):
                node_coords[i, j] = struct.unpack('f', self.reader.read())[0]
        self.mesh.nodes = node_coords

        a = self.reader.search_block('PLT_DOMAIN_SECTION')

        # NOTE: index starts from 0 (in .feb file, index starts from 1)
        idomain = 1
        while self.reader.check_block('PLT_DOMAIN'):
            a = self.reader.search_block('PLT_DOMAIN')

            a = self.reader.search_block('PLT_DOMAIN_HDR')

            a = self.reader.search_block('PLT_DOM_ELEM_TYPE')
            dom_elem_type = int(struct.unpack('I', self.reader.read())[0])

            a = self.reader.search_block('PLT_DOM_PART_ID')
            dom_part_id = (int(struct.unpack('I', self.reader.read())[0]))

            a = self.reader.search_block('PLT_DOM_ELEMS')
            dom_n_elems = (int(struct.unpack('I', self.reader.read())[0]))

            #
            # a = self.reader.search_block('PLT_DOM_NAME')
            # dom_names = (self.reader.read(a).decode("utf-8",errors="ignore"))
            # print(dom_names)
            #print(dom_elem_type,dom_part_id,dom_n_elems)

            elemDict = dict()
            #domainDict['elements'] = dict()
            a = self.reader.search_block('PLT_DOM_ELEM_LIST')
            #print(dom_elem_type,dom_mat_ids,dom_n_elems)
            ne = nodesPerElement[elemType[dom_elem_type]]
            ##print(ne)

            #elements = dict()
            while self.reader.check_block('PLT_ELEMENT'):
                a = self.reader.search_block('PLT_ELEMENT', print_tag=0)
                element = zeros(ne + 1, dtype=int)
                for j in range(ne + 1):
                    element[j] = struct.unpack('I', self.reader.read())[0]
                elemDict[element[0]] = element[1:]
                #elements.append(element)#[1:]
            #domainDict['elements'] = elements
            #dom_elements.append(elements)
            if(dom_part_id in self.mesh.domain.keys()):
                #print("TRUE")
                self.mesh.domain[dom_part_id]['elements'].update(elemDict)
                self.mesh.domain[dom_part_id]['nElems'] = dom_n_elems+self.mesh.domain[dom_part_id]['nElems']
            else:
                domainDict = {'elemType' : elemType[dom_elem_type], 'partID' : dom_part_id, 'nElems' : dom_n_elems, 'elements' : elemDict}
                #keyName = list(self.mesh.parts.keys())[list(self.mesh.parts.values()).index(dom_part_id)]
                self.mesh.domain[dom_part_id] = domainDict
            idomain+=1
            #self.mesh.elements.append(domainDict)


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

                a = self.reader.search_block('PLT_SURFACE_NAME')
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
                self.mesh.surface[surface_ids] = {'name' : surface_names,
                                                    'nFaces' : surface_faces,
                                                    'nNodesPerFacet' : face_max_facet_nodes,
                                                    'faces' : facesDict
                                                    }
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
                        #"element[j] = struct.unpack('I', f.read(4))[0]
                        nodes.append(struct.unpack('I', self.reader.read())[0])
                    #elements.append(element)
                self.mesh.nodeset[nodeset_ids] = {
                                                    'name' : nodeset_names,
                                                    'nodeNumber' : nodeset_nodes,
                                                    'nodes' : nodes
                                                    }

    def readParts(self):
        a = self.reader.search_block('PLT_PARTS_SECTION')
        while self.reader.check_block('PLT_PART'):
            a = self.reader.search_block('PLT_PART')
            a = self.reader.search_block('PLT_PART_ID')
            partID = (struct.unpack('I', self.reader.read())[0])
            a = self.reader.search_block('PLT_PART_NAME')
            partName = (self.reader.read(a).decode("utf-8",errors="ignore").split('\x00')[0])
            #print(partID,partName)
            self.mesh.parts[partName] = partID

        #print(self.mesh.parts)

    def readDict(self):

        self.itemType = {0 : 'FLOAT', 1: 'VEC3F', 2 : 'MAT3FS', 3 : 'MAT3FD', 4 : 'TENS4FS', 5 : 'MAT3F'}
        #https://github.com/febiosoftware/FEBio/blob/master/Documentation/FEBioBinaryDatabaseSpecification.pdf
        self.itemStorageFmt = {0 : 'NODE', 1: 'ITEM', 2 : 'MULT', 3 : 'REGION', 4 : 'MATPOINTS'}
        #https://github.com/febiosoftware/FEBio/blob/f9a3cdd74d1864ec0886decc918ef8e805344fbc/FECore/fecore_enum.h
        self.dictionary = dict()
        self.reader.search_block('PLT_DICTIONARY')

        ############### NODAL DICTIONARY ###################
        a = self.reader.search_block('PLT_DIC_NODAL')
        while self.reader.check_block('PLT_DIC_ITEM'):
            a = self.reader.search_block('PLT_DIC_ITEM')
            a = self.reader.search_block('PLT_DIC_ITEM_TYPE')
            item_types = (int(struct.unpack('I', self.reader.read())[0]))
            a = self.reader.search_block('PLT_DIC_ITEM_FMT')
            item_formats = (int(struct.unpack('I', self.reader.read())[0]))
            a = self.reader.search_block('PLT_DIC_ITEM_NAME')
            item_names = (self.reader.read(64).decode("utf-8",errors="ignore").split('\x00')[0])
            self.dictionary[item_names] = {'type' : self.itemType[item_types], 'format' : self.itemStorageFmt[item_formats]}
        ############### NODAL DICTIONARY ###################

        ############### DOMAIN DICTIONARY ###################
        a = self.reader.search_block('PLT_DIC_DOMAIN')
        while self.reader.check_block('PLT_DIC_ITEM'):
            a = self.reader.search_block('PLT_DIC_ITEM')
            a = self.reader.search_block('PLT_DIC_ITEM_TYPE')
            item_types = (int(struct.unpack('I', self.reader.read())[0]))

            a = self.reader.search_block('PLT_DIC_ITEM_FMT')
            item_formats = (int(struct.unpack('I', self.reader.read())[0]))
            #print(item_formats,item_types)
            a = self.reader.search_block('PLT_DIC_ITEM_NAME')
            item_names = (self.reader.read(64).decode("utf-8",errors="ignore").split('\x00')[0])
            self.dictionary[item_names] = {'type' : self.itemType[item_types], 'format' : self.itemStorageFmt[item_formats]}
        ############### DOMAIN DICTIONARY ###################

        ############### SURFACE DICTIONARY ###################
        a = self.reader.search_block('PLT_DIC_SURFACE')
        while self.reader.check_block('PLT_DIC_ITEM'):
            a = self.reader.search_block('PLT_DIC_ITEM')
            a = self.reader.search_block('PLT_DIC_ITEM_TYPE')
            item_types = (int(struct.unpack('I', self.reader.read())[0]))
            a = self.reader.search_block('PLT_DIC_ITEM_FMT')
            item_formats = (int(struct.unpack('I', self.reader.read())[0]))
            a = self.reader.search_block('PLT_DIC_ITEM_NAME')
            item_names = (self.reader.read(64).decode("utf-8",errors="ignore").split('\x00')[0])
            self.dictionary[item_names] = {'type' : self.itemType[item_types], 'format' : self.itemStorageFmt[item_formats]}
        ############### SURFACE DICTIONARY ###################

        self.results = dict()

        for key in self.dictionary.keys():
            #self.results[key] = np.array([])
            self.results[key] = []

        self.dictNodal = (sum(np.fromiter((1 for v in self.dictionary.values() if v['format'] == 'NODE') ,dtype=int)))
        self.dictItem = (sum(np.fromiter((1 for v in self.dictionary.values() if v['format'] == 'ITEM') ,dtype=int)))



    def readObjState(self):
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

        a = self.reader.search_block('PLT_OBJECT_DATA')
        a = self.reader.search_block('PLT_DIC_ITEM_TYPE')
        itemType = struct.unpack('I', self.reader.read())[0]
        a = self.reader.search_block('PLT_DIC_ITEM_FMT')
        itemFmt = struct.unpack('I', self.reader.read())[0]

        self.rigidDictionary[objID] = { 'name' : objName,
                                        'tag' : objTAG,
                                        'pos' : [objPOSX,objPOSY,objPOSZ],
                                        'rot' : [objROTX,objROTY,objROTZ,objROTW],
                                        'itemType' : itemType,
                                        'itemFmt' : itemFmt
                                    }

    def skipState(self):
        a = self.reader.seek_block('PLT_STATE')
        self.reader.read(a)

    def readSteps(self,stepList):
        if(self.readMode == 'readAllStates'):
            sys.exit("readSteps[list] is not compatible with readAllStates function")

        for i in range(len(stepList)):
            if(i == 0):
                stepDiff = stepList[i]
            else:
                stepDiff = stepList[i] - stepList[i-1]
            print(stepDiff)
            if(i>0):
                stepDiff-=1

            for skip in range(stepDiff):
                try:
                    self.skipState()
                except:
                    sys.exit("*******************************\n\n"+"Error: No more steps to skip!!!\n\n"+"*******************************")
            self.readState()
        self.readMode = 'readSteps'
            #try:
            #    self.skipState()
            #except:
            #    sys.error("No more states to skip")
        #self.readState()


    def readState(self):

        var = 0

        dataDim = {'FLOAT' : 1, 'VEC3F' : 3, 'MAT3FD' : 3, 'MAT3FS' : 6, 'MAT3F' : 9, 'TENS4FS' : 21}

        # # now extract the information from the desired state
        a = self.reader.search_block('PLT_STATE')
        a = self.reader.search_block('PLT_STATE_HEADER')
        # a = self.reader.search_block('PLT_STATE_HDR_ID')
        # stateID = struct.unpack('I', self.reader.read())[0]
        # print(stateID)

        a = self.reader.search_block('PLT_STATE_HDR_TIME')
        stateTime = struct.unpack('f', self.reader.read())[0]


        a = self.reader.search_block('PLT_STATE_STATUS')
        stateStatus = struct.unpack('I', self.reader.read())[0] #What is state status?
        #print("STATSTATUS",stateStatus)
        if(stateStatus != 0):
            return 1
        self.time.append(stateTime)
        n_node_data = 0
        item_def_doms = []
        a = self.reader.search_block('PLT_STATE_DATA')
        a = self.reader.search_block('PLT_NODE_DATA')
        while self.reader.check_block('PLT_STATE_VARIABLE'):
            a = self.reader.search_block('PLT_STATE_VARIABLE')
            a = self.reader.search_block('PLT_STATE_VAR_ID')
            varID = struct.unpack('I', self.reader.read())[0]
            #print(varID)

            a = self.reader.search_block('PLT_STATE_VAR_DATA')

            a_end = self.reader.file.tell() + a

            #dictKey = list(self.dictionary.keys())[varID-1]
            dictKey = list(self.dictionary.keys())[var]
            #print(dictKey)
            varDataDim = (dataDim[self.dictionary[dictKey]['type']])
            def_doms = []
            #domainData = np.array([])
            domainData = []
            while(self.reader.file.tell() < a_end):
                dom_num = struct.unpack('I', self.reader.read())[0]
                data_size = struct.unpack('I', self.reader.read())[0]
                n_data = int(data_size / varDataDim / 4.0)
                def_doms.append(dom_num - 1)
                #print("dom num:",dom_num)

                #print(dom_num,data_size,n_data)
                #print('number of node data for domain %s = %d' % (dom_num, n_data))
                if n_data > 0:
                    elem_data = zeros([n_data, varDataDim])
                    for i in range(0, n_data):
                        for j in range(0, varDataDim):
                            elem_data[i, j] = struct.unpack('f', self.reader.read())[0]
                domainData.append(elem_data)
                #domainData = np.append(domainData,elem_data)
            self.results[dictKey].append(domainData)
            var+=1
            #self.results[dictKey] = np.append(self.results[dictKey],domainData)
                #print(elem_data)


            item_def_doms.append(def_doms)
        #print(item_def_doms)

        a = self.reader.search_block('PLT_ELEMENT_DATA')
        while self.reader.check_block('PLT_STATE_VARIABLE'):
            a = self.reader.search_block('PLT_STATE_VARIABLE')
            a = self.reader.search_block('PLT_STATE_VAR_ID')
            varID = struct.unpack('I', self.reader.read())[0]+self.dictNodal
            #print(varID)

            a = self.reader.search_block('PLT_STATE_VAR_DATA')

            a_end = self.reader.file.tell() + a

            #dictKey = list(self.dictionary.keys())[varID-1]
            dictKey = list(self.dictionary.keys())[var]
            #print(dictKey)
            varDataDim = (dataDim[self.dictionary[dictKey]['type']])
            def_doms = []
            domainData = []
            #domainData = np.array([])
            while(self.reader.file.tell() < a_end):
                dom_num = struct.unpack('I', self.reader.read())[0]
                data_size = struct.unpack('I', self.reader.read())[0]
                n_data = int(data_size / varDataDim / 4.0)
                def_doms.append(dom_num - 1)
                #print("dom num:",dom_num)

                #print(dom_num,data_size,n_data)
                #print('number of node data for domain %s = %d' % (dom_num, n_data))
                if n_data > 0:
                    elem_data = zeros([n_data, varDataDim])
                    for i in range(0, n_data):
                        for j in range(0, varDataDim):
                            elem_data[i, j] = struct.unpack('f', self.reader.read())[0]
                domainData.append(elem_data)
                #domainData = np.append(domainData,elem_data)
                #print(elem_data)

            item_def_doms.append(def_doms)
            self.results[dictKey].append(domainData)
            var+=1
            #self.results[dictKey] = np.append(self.results[dictKey],domainData)


        a = self.reader.search_block('PLT_FACE_DATA')
        while self.reader.check_block('PLT_STATE_VARIABLE'):
            a = self.reader.search_block('PLT_STATE_VARIABLE')
            a = self.reader.search_block('PLT_STATE_VAR_ID')
            varID = struct.unpack('I', self.reader.read())[0]
            #print(varID,self.dictNodal,self.dictItem)


            a = self.reader.search_block('PLT_STATE_VAR_DATA')

            a_end = self.reader.file.tell() + a

            #dictKey = list(self.dictionary.keys())[varID-1]
            dictKey = list(self.dictionary.keys())[var]
            #print(dictKey)
            varDataDim = (dataDim[self.dictionary[dictKey]['type']])
            #print(varDataDim)
            def_doms = []
            domainData = []
            #domainData = np.array([])
            while(self.reader.file.tell() < a_end):
                dom_num = struct.unpack('I', self.reader.read())[0]
                data_size = struct.unpack('I', self.reader.read())[0]
                n_data = int(data_size / varDataDim / 4.0)
                def_doms.append(dom_num - 1)
                #print("dom num:",dom_num)

                #print(dom_num,data_size,n_data)
                #print('number of node data for domain %s = %d' % (dom_num, n_data))
                if n_data > 0:
                    elem_data = zeros([n_data, varDataDim])
                    for i in range(0, n_data):
                        for j in range(0, varDataDim):
                            elem_data[i, j] = struct.unpack('f', self.reader.read())[0]
                #domainData = np.append(domainData,elem_data)
                domainData.append(elem_data)
                #print(domainData)
                #domainData = np.array(domainData)
                #print(elem_data)

            item_def_doms.append(def_doms)

            self.results[dictKey].append(domainData)
            var+=1
            #self.results[dictKey] = np.append(self.results[dictKey],domainData)
        return 0


    def readAllStates(self):
        if(self.readMode) == 'readSteps':
            sys.exit("readAllStates is not compatible with readSteps[list]!")
        i=1
        while (1):
            try:
                #print(i)

                status = self.readState()
                #print(i,status)
                i+=1
                if(status != 0):
                    break
            except:
                print("FAILEDD")
                break
        self.readMode = 'readAllStates'

    def clearDict(self):
        for key in self.results:
            self.results[key] = np.array(self.results[key])
            #print(self.results[key].shape)

    def read_xplt(self,filename):


        if(int('0x0031', base=16) == struct.unpack('I', self.reader.read())[0]):
            print('Correct FEBio format')
        #else:
            #sys.exit("The provided file is not a valid xplt file")
        self.reader.search_block('PLT_ROOT')
        self.reader.search_block('PLT_HEADER')
        self.reader.search_block('PLT_HDR_VERSION')
        self.version = struct.unpack('I', self.reader.read())[0]

        self.reader.search_block('PLT_HDR_COMPRESSION')
        self.compression = struct.unpack('I', self.reader.read())[0]

        self.readDict()
        self.readMesh()
        self.readParts()
