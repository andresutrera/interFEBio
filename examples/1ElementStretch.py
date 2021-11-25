import interFEBio
import numpy as np
import matplotlib.pyplot as plt

xplt = interFEBio.xplt('jobs/1ElementStretch.xplt')
xplt.readAllStates() #Read all steps in the xplt file.
xplt.clearDict() #Convert the results dictionary in a numpy array (after reding the desired states)

print("Results dictionary:")
print(xplt.dictionary) #Print the dictionary of results

print()
print("List of regions:",xplt.listRegions())
print("List of surfaces:",xplt.listSurfaces()) #There is no surfaces defined in this simulation
print("List of nodesets:",xplt.listNodesets())


#Pick a node of the prescribed displacement nodeset
node = xplt.mesh.nodeset[xplt.nodesetID('PrescribedDisplacement1')]['nodes'][0]

print("node of the displaced face:", node)
displacementInTime = xplt.results['displacement'][:,0,node,2] #All times, region 0, node, z cooridnate
print("Displacement of the node {} in time: {}".format(node,displacementInTime))

#Both lagrange strain and stress are element results.
strain = xplt.results['Lagrange strain'][:,0,0,2] #All times, region 0, element 0, z cooridnate (voigt notation)
stretch = np.sqrt(2*strain+1) # E = 0.5(C-I); stretch=sqrt(C)
stress = xplt.results['stress'][:,0,0,2]*1000 #MPa to kPa

#Plot of the stress-stretch curve over the simulation.
plt.xlabel('Stretch $\lambda$')
plt.ylabel('Stress $\sigma$ [kPa]')
plt.plot(stretch,stress)
plt.show()
