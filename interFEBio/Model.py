"""
Module that defines and provides means for outputting the XML format .feb file.

Creating the object will initialize a skeleton of the model tree
"""
from . import Mesh,Step,Material,LoadData,Output,Globals,Constraints
import xml.etree.cElementTree as ET



class Model():
    """
    Create a model object.

    Args:
    ----------

        vers(str)       :   Spec version for the .feb output. Default = '3.0'
                            This library doesnt allow to write in different spec versions.

        modelfile(str)  :   Filename for the generated model file.

        encode(str)     :   Encoding for the .feb xml file. Default = "ISO-8859-1"

        steps(list)     :   list of dictionaries containing the steps of the analysis.
                            The format of each step is 'step name' : 'type'.
                                >>> steps=[{'Step01': 'solid'}, {'Step02': 'solid'}]
    """


    def __init__(self,vers='4.0',modelfile="default.feb",encode="ISO-8859-1"):
        '''
        Constructor
        '''
        self.modelfile = modelfile
        self.encode = encode
        self.root = ET.Element("febio_spec",version=vers)
        self.firstModule = ET.SubElement(self.root,"Module", type='solid')
        self.globals = ET.SubElement(self.root,"Globals")
        self.material = ET.SubElement(self.root,"Material")
        self.mesh = ET.SubElement(self.root,"Mesh")
        self.meshDomains = ET.SubElement(self.root,"MeshDomains")
        self.meshData = ET.SubElement(self.root,"MeshData")
        self.Steps = ET.SubElement(self.root,"Step")
        self.loadData = ET.SubElement(self.root,"LoadData")
        self.output = ET.SubElement(self.root,"Output")
        self.plotVars = ET.SubElement(self.output,"plotfile", type='febio')

        self.addOutput(Output.plotVar('displacement'))
        self.addOutput(Output.plotVar('stress'))
        self.addOutput(Output.plotVar('relative volume'))

    def addGlobals(self, globals:Globals = Globals.Constants()):
        self.globals.append(globals.tree())

    def addMesh(self,msh: Mesh):
        self.mshObject = msh
        self.mesh.append(msh.getNodeTree()) #Write node tree

        for elset in msh.getElementTree():#Write element tree
            self.mesh.append(elset)
        for fset in msh.getSurfaceTree():#Write surface sets
            self.mesh.append(fset)    
        for nset in msh.getNodesetTree():#Write surface sets
            self.mesh.append(nset)    
            
        for name,pair in self.mshObject.surfacePairs.items():
            surfPair = ET.Element("SurfacePair", name=name)
            ET.SubElement(surfPair,"primary").text = pair[0]
            ET.SubElement(surfPair,"secondary").text = pair[1]

            self.mesh.append(surfPair) #Write node tree

        for meshData in self.mshObject.meshData:
            self.meshData.append(meshData.getroot())

    def addStep(self,stp: Step.Step = None):
        self.Steps.append(stp.tree())

    def addMaterial(self,material:Material = None):
        self.material.append(material.tree())
        self.addMeshDomain(material)

    def addMeshDomain(self, material:Material = None):
        type = self.mshObject.elsets[material.elementSet]['type']
        if type in ['quad4', 'tri3']:
            shellDom = ET.SubElement(self.meshDomains, 'ShellDomain', name=material.elementSet, mat=material.name)
            #ET.SubElement(shellDom, 'shell_normal_nodal').text = '1' ############ This was randomly deleted. Maybe is an error
        else:
            ET.SubElement(self.meshDomains, 'SolidDomain', name=material.elementSet, mat=material.name)        

    def addLoadData(self, loadData: LoadData = LoadData.loadController()):
        self.loadData.append(loadData.tree())
    
    def addOutput(self, output:Output = None ):
        self.plotVars.append(output.tree())


    def writeModel(self):
        """
        Write the .feb model file

        """
        # Assemble XML tree
        tree = ET.ElementTree(self.root)

        # Make pretty format
        level = 0
        elem = tree.getroot()
        self.__indent(elem,level)

        #Write XML file
        tree.write(self.modelfile,encoding=self.encode)



    def __indent(self,elem,level):
        i = '\n' + level*'    '
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + '    '
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for child in elem:
                    self.__indent(child, level+1)
                if not child.tail or not child.tail.strip():
                    child.tail = i
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
