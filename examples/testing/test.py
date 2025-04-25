import Boundary as Boundary
import LoadData as LoadData
import Output as Output
import Loads as Loads
import Contact as Contact
import Control as Control
import Mesh as Mesh
import Model
import Step
import xml.etree.cElementTree as ET
import Material

# cl = Boundary.prescribedDisplacement(name='PPP',nset = 'sedwg',dof='x',scale=1.0, relative=False, attributes={'scale':{'lc':'1'}})

xsym = Boundary.fixedDisplacement(name='xsym',nset = '@surface:xsym',x_dof=1)
ysym = Boundary.fixedDisplacement(name='ysym',nset = '@surface:ysym',y_dof=1)
zsym = Boundary.fixedDisplacement(name='zsym',nset = '@surface:zsym',z_dof=1)
xdisp = Boundary.prescribedDisplacement(name='xdisp',nset = '@surface:xdisp',dof='x',value=1.0, relative=False, attributes={'value':{'lc':'1'}})


# print(ET.tostring(cl.tree()))

# print(ET.tostring(zd.tree()))



# lc = LoadData.loadController()
# print(ET.tostring(lc.tree()))

# plt = Output.plotVar(name='displacement')
# print(ET.tostring(plt.tree()))


# load = Loads.surface_load(name='surf', surface='asdad', attributes={'pressure':{'lc':1}})

# print(ET.tostring(load.tree()))


# contac = Contact.sliding_elastic(name='zdfsdf',surface_pair='aAAAA',symmetric_stiffness=15)
# print(ET.tostring(contac.tree()))


control = Control.Control()
# print(ET.tostring(control.tree()))


mesh = Mesh.MeshDef('ring.msh','gmsh',physicalEntities=['arteria'])

model = Model.Model()
model.addMesh(mesh)

stp1 = Step.Step()
# stp1.addContact(contac)
stp1.addControl(control)
stp1.addBoundary(xsym)
stp1.addBoundary(ysym)
stp1.addBoundary(zsym)
stp1.addBoundary(xdisp)

model.addStep(stp1)

parameters={'density':1,
            'k':10,
            'G':10E-3}
mat = Material.material(id=1,name='Material1', type='incomp neo-Hookean', elementSet='arteria', parameters=parameters)

model.addMaterial(mat)
model.addLoadData()
model.addGlobals()
model.writeModel()