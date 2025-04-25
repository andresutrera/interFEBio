#############################
# Fitting HGO Material with the constants:
# c = 30E-3
# k1 = 50E-3
# k2 = 0.3
# kappa = 0.2
# gamma = 60
# k = 1000*k1
############################


import interFEBio
import numpy as np
import lmfit

####### FUNCTION TO DETERMINE THE SIMULATION RESULTS #######
####### written in terms of the xplt class
####### self,file arguments are needed.
####### Must return a x,y lists, equivalent to the experimental measurements (xexp,yexp)
####### In this case, the same function works for both simulations, but it could be one function per simulation
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
longExp = np.loadtxt('long.txt')
circExp = np.loadtxt('circ.txt')
fit.addCase('long',1,'long.feb','long',longExp,simResult)
fit.addCase('circ','Material1','circ.feb','circ',circExp,simResult)

fit.p.add('c', 20e-3, min=0,max=35e-3)
fit.p.add('k1', 50e-3, min=0,max=55e-3)
fit.p.add('k2', 0.2, min=0,max=0.3)
fit.p.add('kappa', 0.15, min=0.1,max=0.25)
fit.p.add('gamma', 50, min=50, max=70)
fit.p.add('k', expr='1000*c')
#fit.optimize(xtol=1.e-20,ftol=1.e-20,epsfcn=0.02)
fit.optimize(method='basinhopping')
