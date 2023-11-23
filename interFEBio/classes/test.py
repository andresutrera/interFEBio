import Boundary as Boundary
import LoadData as LoadData
import Output as Output
import Loads as Loads

import xml.etree.cElementTree as ET
cl = Boundary.prescribedDisplacement(name='PPP',nset = 'sedwg',dof='x',scale=1.0, relative=False, attributes={'scale':{'lc':'1'}})

zd = Boundary.fixedDisplacement(name='PPP',nset = 'sedwg',x_dof=1)


print(ET.tostring(cl.tree()))

print(ET.tostring(zd.tree()))



lc = LoadData.loadController()
print(ET.tostring(lc.tree()))

plt = Output.plotVar(name='displacement')
print(ET.tostring(plt.tree()))


load = Loads.surface_load(name='surf', surface='asdad', attributes={'pressure':{'lc':1}})

print(ET.tostring(load.tree()))