"""
Module that defines and provides means for outputting the XML format .feb file.

Creating the object will initialize a skeleton of the model tree
"""
from __future__ import print_function
from builtins import str
from builtins import map
from builtins import range
from builtins import object
import xml.etree.cElementTree as ET
import string
import itertools

class Model(object):
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


    def __init__(self,vers='3.0',modelfile="default.feb",encode="ISO-8859-1",steps=[{'Step01': 'solid'}]):
        '''
        Constructor
        '''
        self.modelfile = modelfile
        self.encode = encode
        self.root = ET.Element("febio_spec",version=vers)
        self.firstModule = ET.SubElement(self.root,"Module", type='solid')
        self.material = ET.SubElement(self.root,"Material")
        self.geometry = ET.SubElement(self.root,"Mesh")
        self.meshDomains = ET.SubElement(self.root,"MeshDomains")
        self.nodes = ET.SubElement(self.geometry,"Nodes")
        self.meshData = ET.SubElement(self.root,"MeshData")
        #self.meshData = []
        self.surfaces = []
        self.surfacePairs = []
        self.nodeSets = []
        #self.elements = ET.SubElement(self.geometry,"Elements")
        self.elements = []
        self.output = ET.SubElement(self.root,"Output")
        self.plotfile = ET.SubElement(self.output,"plotfile",type="febio")
        self.initialBoundary = ET.SubElement(self.root,'Boundary')
        self.initialConstraint = ET.SubElement(self.root,"Rigid")
        self.initialContact = ET.SubElement(self.root,"Contact")
        self.stepMain = ET.SubElement(self.root,"Step")
        #self.contactMain = ET.SubElement(self.root,"Step")
        self.steps = []
        self.boundary = []
        self.constraint = []
        self.load = []
        self.contactMain = []
        self.i_rigidConstraint = 1
        cnt = 0
        for i in steps:
            self.steps.append(ET.SubElement(self.stepMain,"step", name=list(i.keys())[0]))
            #ET.SubElement(self.steps[cnt],"Module", type=i[list(i.keys())[0]])
            self.boundary.append(ET.SubElement(self.steps[cnt],"Boundary"))
            self.load.append(ET.SubElement(self.steps[cnt],"Loads"))
            self.constraint.append(ET.SubElement(self.steps[cnt],"Rigid"))
            self.contactMain.append(ET.SubElement(self.steps[cnt],"Contact"))
            cnt += 1

        #Set default output variables depending on module of first step
        mod = steps[0][list(steps[0].keys())[0]]
        if mod == 'solid':
            ET.SubElement(self.plotfile,"var",type="displacement")
            ET.SubElement(self.plotfile,"var",type="stress")
            ET.SubElement(self.plotfile,"var",type="relative volume")
        elif mod == 'biphasic' or mod == 'poro':
            ET.SubElement(self.plotfile,"var",type="displacement")
            ET.SubElement(self.plotfile,"var",type="stress")
            ET.SubElement(self.plotfile,"var",type="effective fluid pressure")
            ET.SubElement(self.plotfile,"var",type="fluid flux")
        else:
            print('ERROR: Sorry the '+mod+' module is not supported at this time. Terminating execution...')
            raise SystemExit


    def addControl(self,ctrl=None,step=0):
        """
        Add a control object to a particular step of the analysis.

        Args:
        ----------

            ctr(control object) :   control object (interFEBio.Control())

            step(int) :             Step for that control object.
        """
        step_ctrl = ET.SubElement(self.steps[step],"Control")

        for i in list(ctrl.control.keys()):
            if ctrl.control[i] is not None:
                ET.SubElement(step_ctrl,i).text = ctrl.control[i]

        step_ctrl_solver = ET.SubElement(step_ctrl,"solver")
        for i in list(ctrl.solver.keys()):
            if ctrl.solver[i] is not None:
                ET.SubElement(step_ctrl_solver,i).text = ctrl.solver[i]

        if len(ctrl.time_stepper) > 0:
            step_ctrl_timeStepper = ET.SubElement(step_ctrl,"time_stepper")
        for i in list(ctrl.time_stepper.keys()):
            if ctrl.time_stepper[i] is not None:
                ET.SubElement(step_ctrl_timeStepper,i).text = ctrl.time_stepper[i]

                # if i == 'linear_solver' or i=='analysis':
                #     ET.SubElement(step_ctrl,i,type = ctrl.attributes[i])
                # elif i == 'time_stepper':
                #     dmy = ET.SubElement(step_ctrl,i)
                #     for j in list(ctrl.attributes[i].keys()):
                #         if j == 'dtmax' and 'lc' in ctrl.attributes[i][j] :
                #             ET.SubElement(dmy, j, lc=ctrl.attributes[i][j].replace("lc=", ""))
                #         else:
                #             ET.SubElement(dmy,j).text = ctrl.attributes[i][j]
                # else:
                #     ET.SubElement(step_ctrl,i).text = ctrl.attributes[i]

    def addOutput(self,output=None):
        """
        Add a output variable to the output section of the .feb file.

        Args:
        ----------

            output(str) : Output variable.
        """
        if output is not None:
            if isinstance(output, list):
                for i in output:
                    ET.SubElement(self.plotfile,"var",type=i)
            else:
                ET.SubElement(self.plotfile,"var",type=output)


    def addMaterial(self,mat=None):
        """
        Add a material to the materials section of the .feb file.

        Args:
        ----------

            mat(MatDef object) : MatDef object.
        """
        if mat is not None:
            levels = []
            for blk in mat.blocks:
                level = blk['branch']
                if level == 0:
                    dmy = ET.SubElement(self.material,blk['btype'],id=str(mat.matid),name=mat.mname,type=mat.mtype)
                    levels.append(dmy)
                    if blk['attributes'] is not None:
                        for i in list(blk['attributes'].keys()):
                            if isinstance(blk['attributes'][i], list):
                                if 'vector' == blk['attributes'][i][0]:
                                    dmy2 = ET.SubElement(dmy, i, type=blk['attributes'][i][0])
                                    ET.SubElement(dmy2, "a").text = blk['attributes'][i][1]
                                    ET.SubElement(dmy2, "d").text = blk['attributes'][i][2]
                                else:
                                    ET.SubElement(dmy,i,type=blk['attributes'][i][0]).text = blk['attributes'][i][1]
                            else:
                                ET.SubElement(dmy,i).text = blk['attributes'][i]
                    continue
                elif level > len(levels) - 1:
                    dmy = ET.SubElement(levels[level-1],blk['btype'])
                    levels.append(dmy)
                else:
                    dmy = ET.SubElement(levels[level-1],blk['btype'])
                if blk['mtype'] is not None:
                    dmy.attrib['type'] = blk['mtype']

                if blk['attributes'] is not None:
                    for i in list(blk['attributes'].keys()):
                        if isinstance(blk['attributes'][i], list):
                            if 'vector' == blk['attributes'][i][0]:
                                dmy2 = ET.SubElement(dmy, i, type=blk['attributes'][i][0])
                                ET.SubElement(dmy2, "a").text = blk['attributes'][i][1]
                                ET.SubElement(dmy2, "d").text = blk['attributes'][i][2]
                            else:
                                ET.SubElement(dmy,i,type=blk['attributes'][i][0]).text = blk['attributes'][i][1]
                        else:
                            ET.SubElement(dmy,i).text = blk['attributes'][i]



    def addGeometry(self,mesh=None,mats=None):
        """
        Add a material to the materials section of the .feb file.

        Args:
        ----------

            mesh(MeshDef object) : MeshDef object.

            mats(list) : List of MatDef object to be used in the geometry.

        """
        if mesh is not None:
            if mats is not None:
                for i in range(len(mesh.nodes)):
                    ET.SubElement(self.nodes, "node", id=str(i + 1)).text = (
                        ",".join(list(map(str, mesh.nodes[i+1]))))
                '''

                for i, e in enumerate(mesh.elements):
                    for m in mats:
                        for es in m.elsets:
                            if e[1] in mesh.elsets[es]:
                                #mesh.elsets[es][e[1]]
                                matid = m.matid
                                break
                        else:
                            continue
                        break
                    ET.SubElement(self.elements,e[0],id=str(i+1),mat=str(matid)).text = string.join(map(str,mesh.elements[i][2:]),',')
                '''

                for i,es in enumerate(mesh.elsets):
                    #print(mesh.elsets)
                    elemType = mesh.elsets[es]['type']
                    self.elements.append(ET.SubElement(self.geometry,"Elements",type=elemType, name=es))
                    for j,element in enumerate(mesh.elsets[es]['elements']):
                        text = ",".join(list(map(str, mesh.elements[element]['nodes'])))
                        ET.SubElement( self.elements[i], "elem", id=str(element+1) ).text = text

                for i,surf in enumerate(mesh.fsets):
                    self.surfaces.append(ET.SubElement(self.geometry,"Surface",name=surf))
                    for j,elem in enumerate(mesh.fsets[surf]['elements']):
                        text = ",".join(list(map(str, elem)))
                        ET.SubElement(self.surfaces[i], mesh.fsets[surf]['type'], id=str(j + 1)).text = text

                for mat in mats:
                    for elset in mat.elsets:
                        type = mesh.elsets[elset]['type']
                        if type in ['quad4', 'tri3']:
                            shellDom = ET.SubElement(self.meshDomains, 'ShellDomain', name=elset, mat=mat.mname)
                            ET.SubElement(shellDom, 'shell_normal_nodal').text = '1'
                        else:
                            ET.SubElement(self.meshDomains, 'SolidDomain', name=elset, mat=mat.mname)

            if mesh.elementData:
                #self.meshData = ET.SubElement(self.root,"MeshData")
                self.febElemData = []
                for data in mesh.elementData:
                    self.febElemData.append(ET.SubElement(self.meshData,"ElementData"))
                    for attrib in data['attrubutes']:
                        self.febElemData[-1].set(attrib, str(data['attrubutes'][attrib]))

                    for datai in data['tree']:
                        self.febElemData[-1].insert(0, datai)
            # if mesh.elementdata:
            #     self.elementdata = ET.SubElement(self.geometry,"ElementData")
            #     for i in list(mesh.elementdata.keys()):
            #         dmy = ET.SubElement(self.elementdata,"element",id=str(i))
            #         for j in mesh.elementdata[i]:
            #             ET.SubElement(dmy,list(j.keys())[0]).text = j[list(j.keys())[0]]

        else:
            print('WARNING: No Geometry added. You need to specify a mesh and/or material object')



    def addBoundary(self,boundary=None):
        """
        Add boundary to the .feb file.

        Args:
        ----------

            boundary(Boundary object) : Boundary object containing the boundary at each step.

        """
        if boundary is not None:
            self.prescribedblk = []
            self.prescribedrelblk = []
            self.contactblk = []
            self.springblk = []

            self.i_fixed = 1
            self.i_prescribed = 1
            self.i_rigid = 1
            self.i_sliding_node_on_facet = 1
            self.i_sliding_facet_on_facet = 1
            self.i_sliding_elastic = 1
            self.i_tied_node_on_facet = 1
            self.i_tied_facet_on_facet = 1
            self.i_tied_elastic = 1
            self.i_contact_potential = 1
            self.i_sticky = 1
            self.i_periodic_boundary = 1
            self.i_rigid_wall = 1
            self.i_rigid_sphere = 1
            self.i_rigid_joint = 1

            for i in range(len(boundary.bcs)):
                step = boundary.bcs[i]
                if len(step['fixed']) > 0:
                    for i,stepFixed in enumerate(step['fixed']):
                        bcName = 'FixedDisplacement'+str(self.i_fixed)
                        if(stepFixed[0] == 'nodeset'):
                            bcNodeSet = '@surface:'+stepFixed[1]
                        elif(stepFixed[0] == 'node'):
                            bcNodeSet = bcName
                            self.nodeSets.append(ET.SubElement(self.geometry,"NodeSet",name=bcName))
                            ET.SubElement(self.nodeSets[-1], 'n', id=str(stepFixed[1]))
                        self.fixedblk = ET.SubElement(self.initialBoundary,'bc', name=bcName, type='fix', node_set=bcNodeSet)
                        ET.SubElement(self.fixedblk,'dofs').text = stepFixed[2]
                        self.i_fixed+=1

                if len(step['prescribed']) > 0:
                    for j,stepPrescribed in enumerate(step['prescribed']):
                        bcName = 'PrescribedDisplacement'+str(self.i_prescribed)
                        if(stepPrescribed[0] == 'nodeset'):
                            bcNodeSet = '@surface:'+stepPrescribed[1]
                        elif(stepPrescribed[0] == 'node'):
                            bcNodeSet = bcName
                            self.nodeSets.append(ET.SubElement(self.geometry,"NodeSet",name=bcName))
                            ET.SubElement(self.nodeSets[-1], 'n', id=str(stepPrescribed[1]))
                        self.prescribedblk.append(ET.SubElement(self.boundary[i],'bc', name=bcName, type='prescribe', node_set=bcNodeSet))
                        ET.SubElement(self.prescribedblk[-1],'dof').text = stepPrescribed[2]
                        ET.SubElement(self.prescribedblk[-1],'scale', lc=stepPrescribed[3]).text = stepPrescribed[4]
                        ET.SubElement(self.prescribedblk[-1],'relative').text = '0'
                        self.i_prescribed+=1

                    #for b in step['prescribed']:
                    #    ET.SubElement(self.prescribedblk[-1],'node',id=str(b[0]),bc=str(b[1]),lc=str(b[2])).text = str(b[3])

                if len(step['prescribed relative']) > 0:
                    for j,stepPrescribed in enumerate(step['prescribed relative']):
                        bcName = 'PrescribedDisplacement'+str(self.i_prescribed)
                        if(stepPrescribed[0] == 'nodeset'):
                            bcNodeSet = '@surface:'+stepPrescribed[1]
                        elif(stepPrescribed[0] == 'node'):
                            bcNodeSet = bcName
                            self.nodeSets.append(ET.SubElement(self.geometry,"NodeSet",name=bcName))
                            ET.SubElement(self.nodeSets[-1], 'n', id=str(stepPrescribed[1]))
                        self.prescribedblk.append(ET.SubElement(self.boundary[i-1],'bc', name=bcName, type='prescribe', node_set=bcNodeSet))
                        ET.SubElement(self.prescribedblk[-1],'dof').text = stepPrescribed[2]
                        ET.SubElement(self.prescribedblk[-1],'scale', lc=stepPrescribed[3]).text = str(stepPrescribed[4])
                        ET.SubElement(self.prescribedblk[-1],'relative').text = '1'
                        self.i_prescribed+=1

                contactAttribDict = dict()
                contactAttribDict['sliding-facet-on-facet'] = {'laugon' :          0,
                                                                'tolerance' :       0.2,
                                                                'penalty' :         1,
                                                                'two_pass' :        0,
                                                                'auto_penalty' :    0,
                                                                'fric_coeff' :      0,
                                                                'fric_penalty' :    0,
                                                                'search_tol' :      0.01,
                                                                'minaug' :          0,
                                                                'maxaug' :          10,
                                                                'gaptol' :          0,
                                                                'seg_up' :          0,
                                                                'update_penalty' :  0,
                                                                'search_radius' :   0   }
                if len(step['contact']) > 0:
                    ET.SubElement(self.plotfile,"var",type="contact gap")
                    ET.SubElement(self.plotfile,"var",type="contact force")
                    cnt = 0
                    for c in step['contact']:

                        # if c['attributes'] is not None:
                        #     for a in list(c['attributes'].keys()):
                        #         ET.SubElement(self.contactblk[cnt],a).text = c['attributes'][a]
                        if c['type']=='sliding-facet-on-facet':
                            contactName = 'FacetOnFacetSliding'+str(self.i_sliding_facet_on_facet)
                            surfacePair = contactName
                            if(i == 0):
                                self.contactblk.append(ET.SubElement(self.initialContact,'contact',type=c['type'], name=contactName, surface_pair=surfacePair))
                            else:
                                self.contactblk.append(ET.SubElement(self.contactMain[i-1],'contact',type=c['type'], name=contactName, surface_pair=surfacePair))
                            if(type(c['attributes']) is dict):
                                contactAttribDict[c['type']].update(c['attributes'])
                            for attrib in list(contactAttribDict[c['type']].keys()):
                                ET.SubElement(self.contactblk[cnt],attrib).text = str(contactAttribDict[c['type']][attrib])
                            self.surfacePairs.append(ET.SubElement(self.geometry,"SurfacePair",name=contactName))
                            ET.SubElement(self.surfacePairs[-1],"primary").text = c['master']
                            ET.SubElement(self.surfacePairs[-1],"secondary").text = c['slave']

                        cnt += 1

                # if len(step['spring']) > 0:
                #     for b in step['spring']:
                #         if b['stype'] == 'linear':
                #             self.springblk.append(ET.SubElement(self.initialBoundary,'spring',type=b['stype']))
                #             ET.SubElement(self.springblk[-1],'node').text=str(b['n1'])+','+str(b['n2'])
                #             ET.SubElement(self.springblk[-1],'E').text=str(b['E'])


    def addLoad(self,load=None):
        """
        Add load to the .feb file.

        Args:
        ----------

            load(Load object) : Load object containing the loads at each step.

        """
        if load is not None:
            self.forceblk = []
            self.pressureblk = []
            self.tractionblk = []
            self.ffluxblk = []
            self.sfluxblk = []
            self.bfblk = []

            self.i_force = 1
            self.i_pressure = 1
            self.i_traction = 1
            self.i_fflux = 1
            self.i_sflux = 1
            self.i_bodyForce = 1

            for i in range(len(load.loads)):
                step = load.loads[i]
                if len(step['force']) > 0:
                    self.forceblk.append(ET.SubElement(self.load[i],"force"))
                    for f in step['force']:
                        ET.SubElement(self.forceblk[-1],"node",id=str(f[0]),bc=str(f[1]),lc=str(f[2])).text = str(f[3])

                if len(step['pressure']) > 0:
                    for p in step['pressure']:
                        pressureName = 'PressureLoad'+str(self.i_pressure)
                        self.pressureblk.append(ET.SubElement(self.load[i],"surface_load", type='pressure', name=pressureName, surface=p['surface']))
                        ET.SubElement(self.pressureblk[-1],"pressure", lc=p['lc']).text = str(p['pressure'])
                        ET.SubElement(self.pressureblk[-1],"linear").text = str(int(p['linear']))
                        ET.SubElement(self.pressureblk[-1],"symmetric_stiffness").text = str(int(p['symmetric']))
                        ET.SubElement(self.pressureblk[-1],"shell_bottom").text = str(int(p['shellBottom']))

                if len(step['normal_traction']) > 0:
                    cnt = 0
                    for t in step['normal_traction']:
                        self.tractionblk.append(ET.SubElement(self.load[i],"normal_traction",traction=t['traction']))
                        for s in t['surface']:
                            ET.SubElement(self.tractionblk[cnt],s[0],id=str(s[1]),lc=t['lc'],scale=t['scale']).text = ",".join(list(map(str,s[2:])))
                        cnt += 1

                if len(step['fluidflux']) > 0:
                    cnt = 0
                    for ff in step['fluidflux']:
                        self.ffluxblk.append(ET.SubElement(self.load[i],"fluidflux",type=ff['type'],flux=ff['flux']))
                        for s in ff['surface']:
                            ET.SubElement(self.ffluxblk[cnt],s[0],id=str(s[1]),lc=ff['lc'],scale=ff['scale']).text = ",".join(list(map(str,s[2:])))
                        cnt += 1

                if len(step['soluteflux']) > 0:
                    cnt = 0
                    for sf in step['soluteflux']:
                        self.sfluxblk.append(ET.SubElement(self.load[i],"soluteflux",type=sf['type'],sol=sf['sol']))
                        for s in sf['surface']:
                            ET.SubElement(self.sfluxblk[cnt],s[0],id=str(s[1]),lc=sf['lc'],scale=sf['scale']).text = ",".join(list(map(str,s[2:])))
                        cnt += 1

                if len(step['body_force']) > 0:
                    cnt = 0
                    for bf in step['body_force']:
                        self.bfblk.append(ET.SubElement(self.load[i],"body_force",type=bf['type']))
                        for a in list(bf['attributes'].keys()):
                            if isinstance(bf['attributes'][a],list):
                                ET.SubElement(self.bfblk[cnt],a,lc=bf['attributes'][a][0]).text = str(bf['attributes'][a][1])
                            else:
                                ET.SubElement(self.bfblk[cnt],a).text = str(bf['attributes'][a])

    #TODO: Check constraint format in spec 3.0
    # def addConstraint(self,step=None,matid=None,dof=None,type=None, lc=None,scale=None,relative=None):
    #     if matid is None:
    #         print("WARNING: No material ID was specified.  Skipping constraint definition...")
    #         pass
    #     if dof is None:
    #         print("WARNING: No degree(s) of freedom was specified.  Skipping constraint definition...")
    #         pass
    #     name = "RigidConstraint"+str(self.i_rigidConstraint)
    #     if step == 0 or step is None:
    #         parent = ET.SubElement(self.initialConstraint,"rigid_constraint", name=name, type=type)
    #     else:
    #         parent = ET.SubElement(self.constraint[step-1],"rigid_constraint", name=name, type=type)
    #
    #     ET.SubElement(parent,'rb').text = str(matid)
    #     if ',' in dof:
    #         ET.SubElement(parent,'dofs').text = dof
    #     else:
    #         ET.SubElement(parent,'dof').text = dof
    #     if(type != 'fix'):
    #         ET.SubElement(parent,'value', lc=str(lc)).text = str(scale)
    #         if(relative == 1 or relative == '1'):
    #             reltxt = '1'
    #         else:
    #             reltxt = '0'
    #         ET.SubElement(parent,'relative').text = reltxt




    def addLoadCurve(self,lc=None,lctype='loadcurve',points=[[0,0],[1,1]], interpolate='LINEAR',extend='CONSTANT', math=None,var=None,target=None,Kp=None,Kd=None,Ki=None ):
        """
        Add a load controller to the .feb model.

        Args:
        ----------

            lc(str) :           ID of the load controller.

            lctype(str):        Type of load controller (loadcurve, math, PID)

            points(list):       List of points to be added in a loadcurve type controller.
                                points=[[p1 time, p1 value], [p2 time, p2 value], ...]

            interpolate(str):   Type of interpolation. (STEP, LINEAR, SMOOTH)

            extend(str) :       Type of extend ouside the interval time. (CONSTANT, EXTRAPOLATE, REPEAT, REPEAT OFFSET)

        """
        try:
            self.loaddata
        except:
            self.loaddata = ET.SubElement(self.root,"LoadData")
        if lc is None:
            print("WARNING: No load curve id specified. Assuming default value of 1...")
            lc = '1'
        if lctype is None:
            print("WARNING: No load curve type specified. Assuming default value of linear")
        if(lctype == 'loadcurve'):
            for i,point in enumerate(points):
                if(len(point)%2 != 0):
                    raise ValueError("The point list {} is not even!. Stopping".format(point))
        elif(lctype == 'math'):
            if(math is None ):
                raise ValueError("Math expression cannot be empty")
            if(not isinstance(math, str)):
                raise ValueError("Math expression is not a string")
        elif(lctype == 'PID'):
            if(var is None):
                raise ValueError("The variable name is empty")
            if(not isinstance(var, str)):
                raise ValueError("The variable name is not a string")
            if(Kp is None):
                print("WARNING: Kp is not numerically defined. Assuming default value of 1...")
                Kp = 1
            if(Kd is None):
                print("WARNING: Kd is not numerically defined. Assuming default value of 1...")
                Kd = 1
            if(Ki is None):
                print("WARNING: Ki is not numerically defined. Assuming default value of 1...")
                Ki = 1

        if(lctype == 'loadcurve'):
            loadController = ET.SubElement(self.loaddata,"load_controller",id=lc,type=lctype)
            ET.SubElement(loadController,'interpolate').text = interpolate
            ETpoints = ET.SubElement(loadController,"points")
            for point in points:
                ET.SubElement(ETpoints,'point').text = "{},{}".format(*point)
        elif(lctype == 'math'):
            loadController = ET.SubElement(self.loaddata,"load_controller",id=lc,type=lctype)
            ET.SubElement(loadController,'math').text = math
        elif(lctype == 'PID'):
            loadController = ET.SubElement(self.loaddata,"load_controller",id=lc,type=lctype)
            ET.SubElement(loadController,'var').text = var
            ET.SubElement(loadController,'target').text = target
            ET.SubElement(loadController,'Kp').text = "{}".format(Kp)
            ET.SubElement(loadController,'Kd').text = "{}".format(Kd)
            ET.SubElement(loadController,'Ki').text = "{}".format(Ki)


    # def addGlobal(self,constants=None, solutes=None, generations=None):
    #     try:
    #         self.globals
    #     except:
    #         self.globals = ET.SubElement(self.root,"Globals")
    #     if constants is not None:
    #         try:
    #             for i in list(constants.keys()):
    #                 ET.SubElement(self.constants,i).text = str(constants[i])
    #         except:
    #             self.constants = ET.SubElement(self.globals,"Constants")
    #             for i in list(constants.keys()):
    #                 ET.SubElement(self.constants,i).text = str(constants[i])
    #
    #     if solutes is not None:
    #         try:
    #             cnt = len(self.solutes)
    #             for i in list(solutes.keys()):
    #                 ET.SubElement(self.solutes,"solute",id=str(cnt),name=i).text = str(solutes[i])
    #                 cnt += 1
    #         except:
    #             cnt = 1
    #             self.solutes = ET.SubElement(self.globals,"Solutes")
    #             for i in list(solutes.keys()):
    #                 ET.SubElement(self.solutes,"solute",id=solutes[i][0],name=i).text = str(solutes[i][1])
    #                 cnt += 1
    #
    #     if generations is not None:
    #         try:
    #             cnt = len(self.generations)
    #             for i in generations:
    #                 ET.SubElement(self.generations,"gen",id=str(cnt)).text = str(i)
    #                 cnt += 1
    #         except:
    #             cnt = 1
    #             self.generations = ET.SubElement(self.globals, "Generations")
    #             for i in generations:
    #                 ET.SubElement(self.generations,"gen",id=str(cnt)).text = str(i)
    #                 cnt += 1




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
