import febio

# create a MeshDef object, mesh, reading in simpleblock.inp in abaqus format
mesh = febio.MeshDef('testContact.msh','gmsh',physicalEntities=['Solid','contact'])

# create a Model obect, model, that will be written to test.feb
# NOTE: all steps and modules for those steps are defined here
# default if blank is 1 step with module type "solid"
model = febio.Model(modelfile='contact.feb',steps=[{'Displace': 'solid'}])

#make a material
mat1 = febio.MatDef(matid=1,mname='Material 1',mtype='neo-Hookean',
elsets=['Solid'],attributes={'density': '1.0', 'E': '1000.0','v': '0.3'})
mat2 = febio.MatDef(matid=2,mname='Material 2',mtype='rigid body',
elsets=['contact'],attributes={'density': '1.0', 'center_of_mass': '0,0,0'})

#add the material to the model
model.addMaterial(mat1)
model.addMaterial(mat2)
#make the geometry section of the model
model.addGeometry(mesh=mesh,mats=[mat1,mat2])

#define a loadcurve
model.addLoadCurve(lc='1',lctype='loadcurve',points=[0,0,1,1])

#initialize a boundary condition object
boundary = febio.Boundary(steps=2)
#add a fixed boundary condition to bottom z nodes
boundary.addFixed(nset="zsym",dof='x,y,z')
boundary.addContact(step=1,ctype='sliding-facet-on-facet',master="top",slave="contact",attributes={'auto_penalty' : 1, 'update_penalty' : 1})
model.addConstraint(step=0,matid=2,dof='Rx,Ry,Ru,Rv,Rw',type='fix')
model.addConstraint(step=1,matid=2,dof='Rz',type='prescribe', lc=1,scale=-0.2,relative=0)
#boundary.addFixed(nodeid='2',dof='x,y,z')
#add a prescribed displace to top z nodes for step 1
#boundary.addPrescribed(step=1,nset="trac",dof='z',lc='1',scale='0.1')
#boundary.addPrescribed(step=1,nodeid=[6,24,25,26,7],dof='z',lc='1',scale='0.1')
# #add a relative prescribed displacement to top z nodes for step 2
# boundary.addPrescribed(step=1,nset=mesh.nsets['nzp'],dof='z',lc='2',scale='0.2',ptype='relative')

# #add boundary conditions to model
model.addBoundary(boundary=boundary)
#
#create a control block
ctrl = febio.Control()

#add the control block to the model step 1
model.addControl(step=0,ctrl=ctrl)
#add same control block to step 2


#generate the model file
model.writeModel()
