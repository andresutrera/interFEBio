import interFEBio
import numpy as np
import lmfit
from scipy.interpolate import interp1d

####### FUNCTION TO DETERMINE THE SIMULATION RESULTS #######
####### written in terms of the xplt class
####### self,file arguments are needed.
####### Must return a x,y lists, equivalent to the experimental measurements (xexp,yexp)
def simResult(self,file):
    xplt = interFEBio.xplt(file)
    xplt.readAllStates()
    #disp of all times, region 0, node 1, dir z (2)
    disp = xplt.results['displacement'].getData(domain=0)[:,1,0]
    #stress of all time steps, region 0, element 0, stressZZ (voigt)
    stress = xplt.results['stress'].getData(domain=0)[:,0,0]
    return disp,stress
####### FUNCTION TO DETERMINE THE SIMULATION RESULTS #######


fit = interFEBio.fit()
exp = np.loadtxt('Data pan 0.5.txt')

exp = exp[exp[:,0] >= 0.01]
exp[:,0] = exp[:,0]-exp[0,0]
print(exp[0,1])
exp[:,1] = exp[:,1]-exp[0,1]


# weights  = interp1d([0,0.03,0.03000001,1],[100,100,1,1])
weights  = interp1d([0,1],[1,1])
fit.addCase('fabius',1,'Model1.feb','fabius',exp,simResult,weights)

fit.p.add('c1', 5)
fit.p.add('c2', -100)
fit.p.add('c3', 1200)
fit.p.add('c4', -6000)

fit.p.add('k', expr='1000*c1')
fit.optimize(epsfcn=0.01) #method='BFGS',options={'eps': 0.01}
