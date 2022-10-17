"""
This module is related to material definition.
"""

from __future__ import print_function
from builtins import object

class MatDef(object):
    '''
    Define a material object associated to a particular list of element sets.

    Args:
    ----------

        mtype(str)          : Name of the material model.

        elsets(list/str)    : Name of the element sets associated to this material.

        mname(str)          : Material name.

        matid(int)          : Material ID.

        subattributes(dict) : Subattributes of the material (type, lc, etc...)

    '''

    def __init__(self,mtype=None,elsets=None,mname=None,matid=None,attributes=None, subattributes={}):
        if not matid:
            print("ERROR: You must specify a material id! Terminating execution...")
            raise SystemExit
        self.attributes = attributes
        self.subattributes = subattributes
        self.matid = matid
        self.mtype = mtype
        if isinstance(elsets,list):
            self.elsets = elsets
        else:
            self.elsets = [elsets]
        self.mname = mname
        self.blocks = []
        #create the root material block
        self.addBlock(0,'material')

    def addBlock(self,branch=None,btype=None,mtype=None,attributes=None, subattributes={}):
        '''
        Add block definition to list of blocks in material

        Args:
        ----------

            branch(int)         : Branch level. (0 = root)

            btype(str)          : Block type. (material,solid,fluid,etc.)

            matid(int)          : Material ID. (integer if root, False otherwise)

            attributes(dict)    : Attributes of the material

            subattributes(dict of dicts) : Subattributes of the material ({'type':'map', 'lc':1})
        '''
        if branch == 0:
            attributes = self.attributes
            subattributes = self.subattributes
        blk = {'branch': branch,
               'btype': btype,
               'mtype': mtype,
               'attributes': attributes,
               'subattributes' : subattributes}

        self.blocks.append(blk)

    def appendElset(self,elset):
        '''
        Append a element set to the material

        Args:
        ----------

            elsets(str)    : Name of the element sets.

        '''
        self.elsets.append(elset)
