import interFEBio
import numpy as np


#xplt = interFEBio.xplt('jobs/solid-shell.xplt')
xplt = interFEBio.xplt('ringPS.xplt')
print(xplt.dictionary)
print(xplt.mesh.domain[2])
xplt.readAllStates()



print(xplt.results['stress'].getData(domain = 0)[:,0,0])
print(xplt.results['stress'].getDataTime())


