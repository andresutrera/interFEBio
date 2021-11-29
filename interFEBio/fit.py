import numpy as np
import lmfit
from scipy.interpolate import interp1d
import xml.etree.ElementTree as ET
import os
import subprocess
import threading
import sys
import time
from datetime import datetime
import psutil
from sklearn.metrics import r2_score
import interFEBio
from scipy.ndimage import interpolation
import signal

class caso:
    parameters = []

    def __init__(self,modelName,matID,subFolder,expData,simFcn):
        self.modelName = modelName
        self.modelBinary = modelName.split('.feb')[0]+'.xplt'
        self.matID = matID
        self.subFolder = subFolder
        self.expData = expData
        self.current_directory = os.getcwd()
        self.simFcn = simFcn

    def addParameter(self,param):
        self.parameters.append(param)

    def writeCase(self,params,iter):
        pars = dict(params.valuesdict())
        originalTree = ET.parse(self.modelName)
        tree = originalTree
        root = tree.getroot()
        for material in root.findall('.//material'):
            if(material.attrib['id'] == str(self.matID) or material.attrib['name'] == str(self.matID)):
                for const in material:
                    #print(const.tag, self.parameters)
                    if(const.tag in self.parameters):
                        #print(pars[const.tag])
                        const.text = '{:.20e}'.format(pars[const.tag])
                        #print(const.tag,const.text)
        #print(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder))
        tree.write(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder)+'/'+self.modelName,encoding='ISO-8859-1', xml_declaration=True)

        # for p in pars.keys():
        #     if params[p].expr == None:
        #         tree = originalTree
        #         root = tree.getroot()
        #         for material in root.findall('.//material'):
        #             if(material.attrib['id'] == str(self.matID)):
        #                 for const in material:
        #                     #print(const.tag, self.parameters)
        #                     if(const.tag in self.parameters and const.tag == p):
        #                         #print(pars[const.tag])
        #                         const.text = '{:.20e}'.format(pars[const.tag]*(1+0.05)/1000.0)
        #                     if(const.tag in self.parameters and const.tag != p):
        #                         const.text = '{:.20e}'.format(pars[const.tag]/1000.0)
        #                         #print(const.tag,const.text)
        #         #print(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder))
        #         tree.write(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder,p)+'/'+self.modelName.split('.')[0]+'_'+p+".feb",encoding='ISO-8859-1', xml_declaration=True)

    def verifyFolders(self,iter,p):
        pars = dict(p.valuesdict())
        iterDir = os.path.join(self.current_directory, 'iter'+str(iter))
        if not os.path.exists(iterDir):
            os.makedirs(iterDir)
        simDir = os.path.join(iterDir, self.subFolder)
        if not os.path.exists(simDir):
            os.makedirs(simDir)
        # for par in pars.keys():
        #     if p[par].expr == None:
        #         paramPath = os.path.join(simDir, par)
        #         if not os.path.exists(paramPath):
        #             os.makedirs(paramPath)

    # def simToFunctions(self,iter,parameter):
    #     param = parameter.keys()
    #     stretch,stress = self.rawResults(iter,'')
    #     funSim = dict()
    #     funSim['fx'] = interp1d(stretch, stress,fill_value='extrapolate')
    #     for p in param:
    #         if parameter[p].expr == None:
    #             stretch,stress = self.rawResults(iter,p)
    #             funSim[p] = interp1d(stretch, stress,fill_value='extrapolate')
    #
    #     return funSim
    #
    # def singleSimToFunction(self,iter):
    #     stretch,stress = self.rawResults(iter,'')
    #     funSim = interp1d(stretch, stress,fill_value='extrapolate')
    #     return funSim

    def simResults(self,iter):
        file = 'iter'+str(iter)+'/'+self.subFolder+'/'+self.modelBinary
        x, y = self.simFcn(self,file)
        np.savetxt(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder)+'/result.txt',np.transpose([x, y]))
        return x, y


class fit:

    casos = dict()
    exp = dict()
    done = 0
    thisIter = 0
    disp1 = dict()
    def __init__(self):
        self.iter = 1
        self.p = lmfit.Parameters()
        self.mi = 0 #Used for saving fit results
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = datetime.today().strftime('%d-%m-%Y')
        self.logfileName = 'log_'+current_date+'_'+current_time+'.txt'
        self.len1 = dict()
        signal.signal(signal.SIGINT, self.signal_handler)
        self.pid = dict()

    def addCase(self,name,matID,modelName,subFolder,expData,simFcn):
        self.casos[name] = caso(modelName,matID,subFolder,expData,simFcn)

    def updateParamList(self):
        #os.environ['OMP_NUM_THR        # for par in pars.keys():
        #     if p[par].expr == None:
        #         paramPath = os.path.join(simDir, par)
        #         if not os.path.exists(paramPath):
        #             os.makedirs(paramPath)EADS'] = str(round(psutil.cpu_count()/2/(len(self.p.valuesdict())-1)))
        self.parVals = self.p.valuesdict()
        for key in self.parVals.keys():
            for caso in self.casos:
                self.casos[caso].addParameter(key)

    def run(self,caso,dh):

        if(dh == ''):
            p = subprocess.Popen(["febio3 -i "+self.casos[caso].modelName],shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,cwd=os.path.join('iter'+str(self.iter),self.casos[caso].subFolder)+'/')
            print("Running simulation "+os.path.join('iter'+str(self.iter),self.casos[caso].subFolder)+'/'+self.casos[caso].modelName+ ". PID: ",p.pid)
        else:
            p = subprocess.Popen(["febio3 -i "+self.casos[caso].modelName.split('.')[0]+'_'+dh+'.feb'],shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,cwd=os.path.join('iter'+str(self.iter),self.casos[caso].subFolder,dh)+'/')
            print("Running simulation "+os.path.join('iter'+str(self.iter),self.casos[caso].subFolder)+'/'+self.casos[caso].modelName.split('.')[0]+'_'+dh+'.feb'+ ". PID: ",p.pid)
        self.pid[caso] = p.pid
        p.communicate()
        p.wait()
        #sys.exit()

    def expToFunction(self):
        self.expfcn = dict()
        for caso in self.casos:
            self.expfcn[caso] = interp1d(self.casos[caso].expData[:,0], self.casos[caso].expData[:,1],fill_value='extrapolate')

    def statistics(self,p):
        parameters = dict(p.valuesdict())
        self.r2 = dict()
        for case in self.casos:
            actual = self.expfcn[case](self.results[case][0])
            predict = self.results[case][1]

            R_sq = r2_score(actual, predict)
            self.r2[case] = R_sq

        self.logfile = open(self.logfileName, 'a')
        self.logfile.write('iter '+str(self.iter)+'\t')
        self.logfile.write(datetime.now().strftime("%H:%M:%S")+':\n')
        self.logfile.write('\t'+'r2 = ')
        self.logfile.write(str(self.r2))
        self.logfile.write('\n')
        self.logfile.write('\t'+'Parameters = ')
        self.logfile.write(str(parameters))
        self.logfile.write('\n')
        self.logfile.close()


    def residual(self,p):
        parameter = dict(p.valuesdict())
        for caso in self.casos:
            self.casos[caso].verifyFolders(self.iter,p)
            self.casos[caso].writeCase(p,self.iter)
        #if(self.thisIter != self.iter):
        z = []
        for caso in self.casos:
            t = threading.Thread(target=self.run, args=(caso,''))
            t.start()
            z.append(t)
        for t in z:
           t.join()

        # #sys.exit()
        fun = dict()
        residual = dict()
        self.expToFunction()
        self.results = dict()
        totResid = []

        totResid = np.array([])
        for caso in self.casos:
            x, y = self.casos[caso].simResults(self.iter)
            if(self.iter == 1):
                self.len1[caso] = len(x)

            else:
                if(len(x) != self.len1[caso]):
                    i = self.len1[caso]
                    z = i / len(x)
                    x = interpolation.zoom(x,z)
                    y = interpolation.zoom(y,z)
            residual[caso] = -(self.expfcn[caso](x)-y)
            self.results[caso] = [x,y]
            #self.residual = residual
            #totResid.append(residual[caso])
            totResid = np.append(totResid,residual[caso])
        self.statistics(p)
        return totResid

    def per_iteration(self,pars, iter, resid, *args, **kws):
        print(" ITER ", iter, [[i,pars.valuesdict()[i]] for i in pars.valuesdict()])
        self.iter = iter+3

    def optimize(self,**kwargs):
        self.updateParamList()
        self.mi = lmfit.minimize(self.residual,
                            self.p,
                            **dict(kwargs, iter_cb=self.per_iteration)
                            )
        lmfit.printfuncs.report_fit(self.mi.params, min_correl=0.5)
        print(lmfit.fit_report(self.mi))

    def signal_handler(self,sig, frame):
        print()
        print("***********************************")
        print("***********************************")
        print()
        print('You pressed Ctrl+C!')
        print("Killing the running simulations:")
        print(self.pid)
        print()
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
        sys.exit(0)
