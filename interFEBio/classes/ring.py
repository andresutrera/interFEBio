import interFEBio
import xml.etree.cElementTree as ET
import argparse
import Boundary as Boundary
import LoadData as LoadData
import Output as Output
import Loads as Loads
import Contact as Contact
import Control as Control
import Mesh as Mesh
import Model
import Step
import Rigid
import xml.etree.cElementTree as ET
import Material


mesh = Mesh.MeshDef('ring.msh','gmsh',physicalEntities=['arteria','contactPin'])

# create a Model obect, model, that will be written to test.feb
# NOTE: all steps and modules for those steps are defined here
# default if blank is 1 step with module type "solid"
model = Model.Model(modelfile='ring.feb')
mesh.addSurfacePair(name='pair',primary='contactPin',secondary='contactArtery')

model.addMesh(mesh)
parameters={'density':1,
            'density':1,
            'k':10,
            'G':10E-3}
mat = Material.material(id=1,name='Material1', type='incomp neo-Hookean', elementSet='arteria', parameters=parameters)

mat2 = Material.material(id=2,name='Material2', type='rigid body', elementSet='contactPin', parameters={'density': '1.0', 'center_of_mass': '0,0,0'})


#add the material to the model
model.addMaterial(mat)
model.addMaterial(mat2)

model.addLoadData()
model.addGlobals()

stp1 = Step.Step()
xsym = Boundary.fixedDisplacement(name='xsym',nset = '@surface:xsym',x_dof=1)
ysym = Boundary.fixedDisplacement(name='ysym',nset = '@surface:ysym',y_dof=1)
zsym = Boundary.fixedDisplacement(name='zsym',nset = '@surface:zsym',z_dof=1)
contac = Contact.sliding_elastic(name='contact1',surface_pair='pair',symmetric_stiffness=0)

rigidisp = Rigid.rigidDisplacement(name='disp',material='Material2',dof='y',value=1.0,attributes={'value':{'lc':1}})
rigidFix = Rigid.rigidFixed(name='fix',material='Material2',Rx_dof=1,Rz_dof=1,Ru_dof=1,Rv_dof=1,Rw_dof=1)

stp1.addBoundary(xsym)
stp1.addBoundary(ysym)
stp1.addBoundary(zsym)

control = Control.Control(time_steps=100, step_size=0.01,solver=Control.solver(symmetric_stiffness='non-symmetric'))

stp1.addControl(control)
stp1.addContact(contac)
stp1.addRigid(rigidFix)
stp1.addRigid(rigidisp)

model.addStep(stp1)


#generate the model file
model.writeModel()
