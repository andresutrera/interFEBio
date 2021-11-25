import interFEBio
import numpy as np
import lmfit

####### FUNCTION TO DETERMINE THE SIMULATION RESULTS #######
####### written in terms of the xplt class
####### self,file arguments are needed.
####### Must return a x,y lists, equivalent to the experimental measurements (xexp,yexp)
def simResult(self,file):
    xplt = interFEBio.xplt(file)
    xplt.readAllStates()
    xplt.clearDict()
    #disp of all times, region 0, node 1, dir z (2)
    disp = xplt.results['displacement'][:,0,1,2]
    #stress of all time steps, region 0, element 0, stressZZ (voigt)
    stress = xplt.results['stress'][:,0,0,2]
    return disp,stress
####### FUNCTION TO DETERMINE THE SIMULATION RESULTS #######

fit = interFEBio.fit()
exp = np.loadtxt('exp.txt')
fit.addCase('neohooke',1,'Model1.feb','neohooke',exp,simResult)

fit.p.add('G', 120, min=0)
fit.p.add('k', expr='1000*G')
fit.optimize(xtol=1.e-20,ftol=1.e-20,epsfcn=0.02)
