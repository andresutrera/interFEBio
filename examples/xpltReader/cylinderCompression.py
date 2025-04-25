import interFEBio
import numpy as np
import matplotlib.pyplot as plt

xplt = interFEBio.xplt('jobs/cylinderCompression.xplt')
xplt.readAllStates() #Read all steps in the xplt file.
#xplt.clearDict() #Convert the results dictionary in a numpy array (after reding the desired states)

print("Results dictionary:")
print(xplt.dictionary) #Print the dictionary of results

print()
print("List of regions:",xplt.mesh.listRegions())
print("List of surfaces:",xplt.mesh.listSurfaces()) #There is no surfaces defined in this simulation
print("List of nodesets:",xplt.mesh.listNodesets())

plateID = xplt.mesh.nodesetID('plate')
plateNode = xplt.mesh.nodeset[plateID]['nodes'][0] #Pick some node of the plate nodeset

print()
print("Time:")
print(xplt.time)

print()
plateDisplacement = xplt.results['displacement'][:,0,plateNode,2]#all times, region 0, plateNode, z direction
print("Plate displacement:")
print(plateDisplacement)

print()
print("Plate Force:")
plateForce = xplt.results['contact force'][:,0,0,2]
print(plateForce)

#Plot of the plate force over time
plt.xlabel('Time [s]')
plt.ylabel('plate reaction [N]')
plt.plot(xplt.time,plateForce)
plt.show()
