"""
This module deals with the control section for each time interval.

"""
from builtins import object

class Control(object):
    '''
    Class of the control section.

    '''


    def __init__(self, time_stepper = True):
        """

        Create a Control object to be used at each step.
        it contains self.control, self.solver and self.time_stepper dictionarys
        with the keys and values to write the control branch in the xml .feb file
        at a particular time interval.

        Args
        ----------

            time_stepper (bool): Controls if the automatic time stepper will be used or not.

        Default values
        ----------
            >>> Control:
                    analysis :                  STATIC
                    time_steps :                10
                    step_size :                 0.1
            >>> Solver:
                    max_refs :                  15
                    max_ups :                   10
                    diverge_reform :            1
                    reform_each_time_step :     1
                    dtol :                      0.001
                    etol :                      0.01
                    rtol :                      0
                    lstol :                     0.9
                    min_residual :              1E-20
                    qnmethod :                  BFGS
                    rhoi :                      0
            >>> Time Stepper:
                    dtmin :                     0.01
                    dtmax :                     0.1
                    max_retries :               5
                    opt_iter :                  10


        """
        #Defaults values
        self.control = {'analysis' : 'STATIC',
                        'time_steps': '10',
                        'step_size': '0.1',
                        }
        self.solver = {'max_refs': '15',
                        'max_ups': '10',
                        'diverge_reform' : '1',
                        'reform_each_time_step' : '1',
                        'dtol': '0.001',
                        'etol': '0.01',
                        'rtol': '0',
                        'lstol': '0.9',
                        'min_residual': '1E-20',
                        'qnmethod': 'BFGS',
                        'rhoi' : '0'
        }

        if(time_stepper):
            self.time_stepper = {'dtmin' : '0.01',
                                'dtmax' : '0.1',
                                'max_retries' : '5',
                                'opt_iter' : '10'
            }
        else:
            self.time_stepper = {}

    def setAttributes(self,section,specified):
        """

        Set attribute at a specific control section (control, solver, time_stepper)

        Args
        ----------

            section (str): control, solver, time_stepper.

            specified (dict): dictionary containing the parameters to be assigned at the selected section. {key:value}


        """
        for i in list(specified.keys()):
            if(section == 'control'):
                self.control[i.lower()] = specified[i]
            elif(section == 'solver'):
                self.solver[i.lower()] = specified[i]
            elif(section == 'time_stepper'):
                self.time_stepper[i.lower()] = specified[i]
            else:
                print("Section {} is not a valid control section. Must be control, solver or time_stepper. Skipping attributes".format(section))
