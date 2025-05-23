"""
This module allows to execute flexible fitting procedures, with full control
of the fitting method, variables, calculations and experimental data formats.

# TODO

- LMFIT library works on serial numerical approximations to obtain a jacobian,
     however, when the residual function is time expensive, the fitting process
     is too long. A parallel jacobian calculation is implemented, but it is quite rudimental,
     so is disabled in the source code by now.


"""

import numpy as np
import lmfit
from scipy.interpolate import interp1d
import xml.etree.ElementTree as ET
import os
from shutil import rmtree
import subprocess
import threading
import sys
import time
from datetime import datetime
import psutil
from sklearn.metrics import r2_score,mean_squared_error
from math import sqrt
import interFEBio
from scipy.ndimage import interpolation
import signal
from scipy import interpolate
from prettytable import PrettyTable



class case:
    def __init__(self,name = None,modelName=None,matID=None,subFolder=None,expData=None,simFcn=None,weights=None, isTask=False):

        self.name = name
        self.modelName = modelName
        self.modelBinary = modelName.split('.feb')[0]+'.xplt'
        self.matID = matID
        self.subFolder = subFolder
        self.expData = expData
        self.current_directory = os.getcwd()
        self.simFcn = simFcn
        self.parameters = []
        self.weights = weights
        self.isTask = isTask
        self.parameterTask = {}

        self.originalTree = ET.parse(self.modelName)


        if not isinstance(self.expData, dict):
            self.expData = {'default' : self.expData}
        if not isinstance(self.simFcn, dict):
            self.simFcn = {'default' : self.simFcn}
        if not isinstance(self.weights, dict):
            self.weights = {'default' : self.weights}

    def addParameter(self,param):
        self.parameters.append(param)

    def writeCase(self,params,iter,name):
        pars = dict(params.valuesdict())
        tree = self.originalTree
        root = tree.getroot()
        for material in root.findall('.//material'):
            if(material.attrib['id'] == str(self.matID) or material.attrib['name'] == str(self.matID)):
                for const in material:
                    #print(const.tag, self.parameters)
                    if(const.tag in self.parameters):
                        #print(pars[const.tag])
                        const.text = '{:.20e}'.format(pars[const.tag])
                
                for submat in material.findall('.//*[@type]'):
                    for const in submat:
                        if(const.tag in self.parameters):
                            #print(pars[const.tag])
                            const.text = '{:.20e}'.format(pars[const.tag])                    

# #TODO Incluir childs de material en la busqueda.
#         for material in root.findall('.//elastic'):
#             for const in material:
#                 if(const.tag in self.parameters):
#                     const.text = '{:.20e}'.format(pars[const.tag])
#         for material in root.findall('.//damage'):
#             for const in material:
#                 if(const.tag in self.parameters):
#                     const.text = '{:.20e}'.format(pars[const.tag])


        #Evaluate all the parameter tasks
        for paramTask in self.parameterTask:
            root = self.parameterTask[paramTask](root,pars[paramTask])

        tree.write(os.path.join(self.current_directory, 'iters/iter'+str(iter),self.subFolder)+'/'+name,encoding='ISO-8859-1', xml_declaration=True)


    def verifyFolders(self,iter,p):
        if not os.path.exists('iters'):
            os.makedirs('iters')
        pars = dict(p.valuesdict())
        iterDir = os.path.join(self.current_directory, 'iters/iter'+str(iter))
        if not os.path.exists(iterDir):
            os.makedirs(iterDir)
        simDir = os.path.join(iterDir, self.subFolder)
        if not os.path.exists(simDir):
            os.makedirs(simDir)


    def simResults(self,iter):
        simResults = dict()
        for exp in self.expData:
            file = 'iters/iter'+str(iter)+'/'+self.subFolder+'/'+self.modelBinary
            x, y = self.simFcn[exp](self,file)
            np.savetxt(os.path.join(self.current_directory, 'iters/iter'+str(iter),self.subFolder)+'/'+ exp+'.txt',np.transpose([x, y]))
            simResults[exp] = (x,y)
        return simResults

    def derivativeResults(self,iter,name):
        simResults = dict()
        for exp in self.expData:
            file = 'iters/iter'+str(iter)+'/'+self.subFolder+'/'+name
            x, y = self.simFcn[exp](self,file)
            simResults[exp] = (x,y)
        return simResults

class fit:
    '''
    Class that handles the numerical fitting algotirm.
    This class is based on lmfit library.

    '''
    def __init__(self,skip=0,delete=False):
        self.skip=skip
        self.delete=delete
        self.iter = 1
        self.p = lmfit.Parameters()
        self.mi = 0 #Used for saving fit results
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = datetime.today().strftime('%d-%m-%Y')
        self.logfileName = 'log_'+current_date+'_'+current_time+'.txt'
        self.len1 = dict()
        signal.signal(signal.SIGINT, self._signal_handler)
        self.pid = dict()
        self.pidTask = dict()
        

        self.casos = dict()
        self.tasks = dict()
        self.tasksFcns = dict()
        self.exp = dict()
        self.done = 0
        self.thisIter = 0
        self.disp1 = dict()


        self.parallel = True

        self.bestIter = -1
        self.bestFitRMSE = 1E9999

        self.preserveBestIter = True
        self.preserveIters = False




    def addCase(self,name=None,matID=None,modelName=None,subFolder=None,expData=None,simFcn=None,weights=None):
        '''
        Add a simulation to the fitting algorithm, including all the experimental data
        and how to obtain numerical results for this xplt file.

        Args:
        ----------

            modelName (str): Name of the .feb model

            matID (int/str): id/name of the material to be fitted in that particular .feb file

            subFolder (str): Sub folder to store the simulation at each iteration.

            expData (np array): Array of x,y experimental data associated with the current simulation.

            simFcn (fuinction): Function that handles the result calculation of the simulation. Needs to be written in terms of the xplt class functions.

        '''
        self.casos[name] = case(modelName=modelName,matID=matID,subFolder=subFolder,expData=expData,simFcn=simFcn,weights=weights)

    def addTask(self, name=None,matID=None,modelName=None,subFolder=None):
        self.tasks[name] = case(modelName=modelName,matID=matID,subFolder=subFolder,isTask=True)

    def addTaskFcn(self, name=None, fcn=None):
        self.tasksFcns[name] = fcn


    def _updateParamList(self):
        #os.environ['OMP_NUM_THR        # for par in pars.keys():
        #     if p[par].expr == None:
        #         paramPath = os.path.join(simDir, par)
        #         if not os.path.exists(paramPath):
        #             os.makedirs(paramPath)EADS'] = str(round(psutil.cpu_count()/2/(len(self.p.valuesdict())-1)))
        self.parVals = self.p.valuesdict()
        for key in self.parVals.keys():
            for caso in self.casos:
                self.casos[caso].addParameter(key)
            for caso in self.tasks:
                self.tasks[caso].addParameter(key)               

    def _run(self,caso):

        p = subprocess.Popen(["febio4 -i "+self.casos[caso].modelName+' -o /dev/null'],shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,cwd=os.path.join('iters/iter'+str(self.iter),self.casos[caso].subFolder)+'/')
        print("\tRunning simulation "+os.path.join('iters/iter'+str(self.iter),self.casos[caso].subFolder)+'/'+self.casos[caso].modelName+ ". PID: ",p.pid)
        self.pid[caso] = p.pid
        p.communicate()
        p.wait()
        #sys.exit()

    def _runParallel(self,caso,name):

        p = subprocess.Popen(["febio4 -i "+name+' -o /dev/null'],shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,cwd=os.path.join('iters/iter'+str(self.iter),self.casos[caso].subFolder)+'/')
        print("\tRunning simulation "+os.path.join('iters/iter'+str(self.iter),self.casos[caso].subFolder)+'/'+name+ ". PID: ",p.pid)
        self.pid[caso] = p.pid
        p.communicate()
        p.wait()
        #sys.exit()

    def _runTask(self,caso):

        p = subprocess.Popen(["febio4 -i "+self.tasks[caso].modelName+' -o /dev/null'],shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,cwd=os.path.join('iters/iter'+str(self.iter),self.tasks[caso].subFolder)+'/')
        print("\tRunning simulation "+os.path.join('iters/iter'+str(self.iter),self.tasks[caso].subFolder)+'/'+self.tasks[caso].modelName+ ". PID: ",p.pid)
        self.pidTask[caso] = p.pid
        p.communicate()
        p.wait()
        #sys.exit()

    def addParameterTask(self,case,parameter,task,kind='case'):
        if(kind == 'case'):
            self.casos[case].parameterTask[parameter] = task
        elif(kind == 'task'):
            self.tasks[case].parameterTask[parameter] = task


    def _expToFunction(self):
        self.expfcn = dict()
        for caso in self.casos:
            experimentInterps = dict()
            for exp in self.casos[caso].expData:
                experimentInterps[exp] = interp1d(self.casos[caso].expData[exp][:,0], self.casos[caso].expData[exp][:,1],fill_value='extrapolate')
            self.expfcn[caso] = experimentInterps

    def _statistics(self,p):
        parameters = dict(p.valuesdict())
        self.r2 = dict()
        self.RMSE = 0
        
        for case in self.casos:
            expStatistics = dict()
            for exp in self.casos[case].expData:

                actual = self.expfcn[case][exp](self.results[case][exp][0])
                predict = self.results[case][exp][1]

                R_sq = r2_score(actual, predict)
                expStatistics[exp] = R_sq

                self.RMSE += sqrt(mean_squared_error(actual, predict))
                if(self.RMSE < self.bestFitRMSE):
                    self.bestIter = self.iter
                    self.bestFitRMSE = self.RMSE
                    self.bestParameters = p


            self.r2[case] = expStatistics

        self.logfile = open(self.logfileName, 'a')
        self.logfile.write('iter '+str(self.iter)+'\t')
        self.logfile.write(datetime.now().strftime("%H:%M:%S")+':\n')
        self.logfile.write('\t'+'R-squares: ')
        self.logfile.write(str(self.r2))
        self.logfile.write('\n')
        self.logfile.write('\t'+'RMSE: ')
        self.logfile.write(str(self.RMSE))
        self.logfile.write('\n')

        t = PrettyTable(['Parameter', 'Value'])
        for param in p:
            t.add_row([param, "{0:.15f}".format(p[param].value)])
        # Add a tab before each line of the table
        indented_table = "\n".join("\t" + line for line in t.get_string().splitlines())
        self.logfile.write(indented_table)


        self.logfile.write('\n')
        self.logfile.close()

    def destroyFolder(self,iter):
        dir = os.path.join(os.getcwd(), 'iters/iter'+str(iter))
        print("\tDestroying floder: ",dir)
        rmtree(dir,ignore_errors=True)

    def Jacobian(self,p):

        
        print(p)
        parameters = dict(p.valuesdict())
        eps = 0.05 ##### EPSILON VALUE


        #################################################
        ############### WRITING SIM FILES ###############
        toRun = []
        toRead =  []
        for caso in self.casos:

            self.casos[caso].verifyFolders(self.iter,p)
            name = self.casos[caso].modelName
            toRun.append(name)
            #toRead.append(self.casos[caso].modelBinary)
            self.casos[caso].writeCase(p,self.iter,name)

            for param,value in parameters.items():
                print(p[param].vary)
                if(p[param].vary == True):
                    pCopy = p.copy()
                    pCopy[param].value = p[param].value*(1+eps)
                    name = self.casos[caso].modelName.split(".feb")[0]+"_"+param+".feb"
                    binary = self.casos[caso].modelName.split(".feb")[0]+"_"+param+".xplt"
                    toRun.append(name)
                    toRead.append(binary)
                    self.casos[caso].writeCase(pCopy,self.iter,name)

        #################################################
        ############### WRITING SIM FILES ###############


        #################################################
        ##################### RUN  ######################
            z = []
            for fileName in toRun:
                t = threading.Thread(target=self._runParallel, args=(caso,fileName))
                t.start()
                z.append(t)
            for t in z:
                t.join()
        #################################################
        ##################### RUN  ######################



        ######################################################################
        ########################### READ RESULTS #############################

        self._expToFunction()
        self.results = dict()
        totResid = []

        totResid = np.array([])
        






        for caso in self.casos:
            residualExp = dict()
            for exp in self.casos[caso].expData:
                x, y = self.casos[caso].simResults(self.iter)[exp]

                if(self.iter == 1):
                    self.len1[caso] = len(x)
                else:
                    if(len(x) != self.len1[caso]):
                        i = self.len1[caso]
                        z = i / len(x)
                        x = interpolation.zoom(x,z)
                        y = interpolation.zoom(y,z)
                residualExp[exp] = y
                totResid = np.append(totResid,residualExp[exp])

        nParams = len(toRead)
        print(nParams)

        jac = []
        # print("JAC SIZE: ",jac.shape)
            
            
        for i,binary in enumerate(toRead):
            totResidDerivatives = np.array([])
            residualDerivatives = dict()
            for exp in self.casos[caso].expData:
                x, y = self.casos[caso].derivativeResults(self.iter,binary)[exp]
                if(len(x) != self.len1[caso]):
                    i = self.len1[caso]
                    z = i / len(x)
                    x = interpolation.zoom(x,z)
                    y = interpolation.zoom(y,z)
                residualDerivatives[exp] = y
                totResidDerivatives = np.append(totResidDerivatives,residualDerivatives[exp])

            jac.append((totResidDerivatives-totResid)/eps)
        print(jac)
        jac = np.array(jac)
        print("JACOBIAN: ",jac.shape)
        jac=np.ndarray.flatten(jac)
        print("JACOBIAN: ",jac.shape)


        print(jac,totResid.shape[0] )
        #hes = np.matmul(jac,jac.transpose())
        #print(hes)
        return jac
        
        ######################################################################
        ########################### READ RESULTS #############################        



    def _residual(self,p):
        #print(self.iter)
        parameter = dict(p.valuesdict())


        self.printIter(p,self.iter)

        # if(self.parallel == False):

        for task in self.tasksFcns:
            self.tasks[task].verifyFolders(self.iter,p)
            name = self.tasks[task].modelName
            self.tasks[task].writeCase(p,self.iter,name)

        if(self.iter>self.skip):
            #if(self.iter != 2 and self.iter != 3): #### LM methos iters 1,2 and 3 are the same. Why?
            z = []
            for caso in self.tasks:
                t = threading.Thread(target=self._runTask, args=(caso,))
                t.start()
                z.append(t)
            for t in z:
                t.join()


        for task in self.tasksFcns:
            returnTree = self.tasksFcns[task](self.iter, self.casos, self.tasks)
            self.casos['ring'].originalTree = returnTree


        for caso in self.casos:
            self.casos[caso].verifyFolders(self.iter,p)
            name = self.casos[caso].modelName
            self.casos[caso].writeCase(p,self.iter,name)


        if(self.iter>self.skip):
            #if(self.iter != 2 and self.iter != 3):#### LM methos iters 1,2 and 3 are the same. Why?
            z = []
            for caso in self.casos:
                t = threading.Thread(target=self._run, args=(caso,))
                t.start()
                z.append(t)
            for t in z:
                t.join()



        ######################################################################
        ########################### READ RESULTS #############################

        fun = dict()
        residual = dict()
        self._expToFunction()
        self.results = dict()
        totResid = []

        totResid = np.array([])
        for caso in self.casos:
            simResults = dict()
            residualExp = dict()
            for exp in self.casos[caso].expData:
                x, y = self.casos[caso].simResults(self.iter)[exp]
                simResults[exp] = (x,y)
                if(self.iter == 1):
                    self.len1[caso] = len(x)
                else:
                    if(len(x) != self.len1[caso]):
                        i = self.len1[caso]
                        z = i / len(x)
                        x = interpolation.zoom(x,z)
                        y = interpolation.zoom(y,z)
                residualExp[exp] = -(self.expfcn[caso][exp](x)-y)*self.casos[caso].weights[exp](x)
                totResid = np.append(totResid,residualExp[exp])
            self.results[caso] = simResults
        ######################################################################
        ########################### READ RESULTS #############################

        self._statistics(p)

        if(self.delete == True):
            self.removeDirs()


        return totResid


    def removeDirs(self):
        if(self.iter > 1):
            if(self.preserveIters == False):
                dir = os.path.join(os.getcwd(), 'iters')
                dir_list = os.listdir(dir)
                dir_list = [int(itr.split("iter")[1]) for itr in dir_list]

                if(self.preserveBestIter == True):
                    if(self.bestIter in dir_list):
                        dir_list.remove(self.bestIter)
                
                for iter in dir_list:
                    self.destroyFolder(iter)



    def _per_iteration(self,pars, iter, resid, *args, **kws):
        print()
        print("\tR-squares: ",self.r2)
        print("\tRMSE: ",self.RMSE)
        self.printIterFinal()
        self.iter += 1#iter+3

    def optimize(self,**kwargs):
        '''
        Optimize.

        This function start the optimization algorithm.
        The residual is calculated from the simulation (using the external function provided for the case), and compare those results with the experimental data provided.


        kwargs:
        ----------

            kwargs for the lmfit.minimize function.
            >>> optimize(method='basinhopping')
        '''
        self._updateParamList()
        self.initMsg()

        # self.Jacobian(self.p)

        self.mi = lmfit.minimize(self._residual,
                            self.p,
                            **dict(kwargs,iter_cb=self._per_iteration)
                            )
        lmfit.printfuncs.report_fit(self.mi.params, min_correl=0.5)
        print(lmfit.fit_report(self.mi))

    def _signal_handler(self,sig, frame):
        print()
        print("***********************************")
        print("***********************************")
        #print()
        print('You pressed Ctrl+C!')
        print("Killing the following simulations:")
        print(self.pid)
        print(self.pidTask)
        #print()
        print("***********************************")
        print("***********************************")


        for key in self.pid:
            try:
                parent = psutil.Process(self.pid[key])
            except:
                continue
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                try:
                    child.kill()
                except:
                    print("Child process no longer exists.")
                    continue
            try:
                parent.kill()
            except:
                print("Parent process no longer exists.")
                continue


        for key in self.pidTask:
            try:
                parent = psutil.Process(self.pidTask[key])
            except:
                continue
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                try:
                    child.kill()
                except:
                    print("Child process no longer exists.")
                    continue
            try:
                parent.kill()
            except:
                print("Parent process no longer exists.")
                continue

        sys.exit(0)


    def printParameters(self,p):
        t = PrettyTable(['Parameter', 'Value'])
        for param in p:
            t.add_row([param, "{0:.15f}".format(p[param].value)])
        # Add a tab before each line of the table
        indented_table = "\n".join("\t" + line for line in t.get_string().splitlines())
        print(indented_table)

    def initMsg(self):
        print(" _       _            _____ _____ ____  _      ") 
        print("(_)_ __ | |_ ___ _ __|  ___| ____| __ )(_) ___  ")
        print("| | '_ \| __/ _ \ '__| |_  |  _| |  _ \| |/ _ \ ")
        print("| | | | | ||  __/ |  |  _| | |___| |_) | | (_) |")
        print("|_|_| |_|\__\___|_|  |_|   |_____|____/|_|\___/ ")
        print("                                                ")

    def printIter(self,p,iter):
        print("*************************************************")
        print("ITER ",str(iter))
        print("\tCurrent Parameters:")

        self.printParameters(p)
        print()

    def printIterFinal(self):
        print("*************************************************")
        print()