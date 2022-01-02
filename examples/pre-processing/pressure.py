import interFEBio

mesh = interFEBio.MeshDef('pressure.msh','gmsh',physicalEntities=['Solid'])
model = interFEBio.Model(modelfile='pressure.feb',steps=[{'Pressure': 'solid'}])
mat1 = interFEBio.MatDef(matid=1,mname='Material 1',mtype='incomp neo-Hookean',
elsets=['Solid'],attributes={'density': '1.0', 'G': '30E-3','k': '30'})
model.addMaterial(mat1)
model.addGeometry(mesh=mesh,mats=[mat1])

model.addLoadCurve(lc='1',lctype='math', math='1*t')

boundary = interFEBio.Boundary(steps=1)
boundary.addFixed(nset="xsym",dof='x')
boundary.addFixed(nset="ysym",dof='y')
boundary.addFixed(nset="zsym",dof='z')

load = interFEBio.Load(steps=1)
load.addPressure(step=0,surface='pressure',lc='1',pressure=10E-3, linear=False, symmetric=False)
model.addBoundary(boundary=boundary)
model.addLoad(load=load)

ctrl = interFEBio.Control()
ctrl.setAttributes('control', {'time_steps': '20', 'step_size': '0.05'})
ctrl.setAttributes('time_stepper', {'dtmin' : '0.001', 'dtmax' : '0.05'})
model.addControl(step=0,ctrl=ctrl)

model.writeModel()
