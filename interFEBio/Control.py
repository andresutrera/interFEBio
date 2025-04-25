"""
This module deals with boundary conditions
https://github.com/febiosoftware/FEBioStudio/blob/develop/FEMLib/FEBoundaryCondition.cpp

"""
from typing import Literal
from typing import Optional,Union
import xml.etree.cElementTree as ET
from .dataClass import _var,sectionAttribs

class BFGS():
    def __init__(self,
                 max_ups            : int|str = 10,
                 max_buffer_size    : int|str = 0,
                 cycle_buffer       : int|str = 1,
                 cmax               : int|str = 100000,
                 ):
        self.type = 'BFGS'
        self.atr = sectionAttribs()
        self.atr.addAttrib(_var('max_ups',max_ups) )
        self.atr.addAttrib(_var('max_buffer_size',max_buffer_size) )
        self.atr.addAttrib(_var('cycle_buffer',cycle_buffer) )
        self.atr.addAttrib(_var('cmax',cmax) )

    def tree(self):
        tree = ET.Element('qn_method', type=self.type)
        self.atr.fillTree(tree)
        return tree          

class Broyden():
    def __init__(self,
                 max_ups            : int|str = 10,
                 max_buffer_size    : int|str = 0,
                 cycle_buffer       : int|str = 1,
                 cmax               : int|str = 100000,
                 ):
        self.type = 'Broyden'
        self.atr = sectionAttribs()
        self.atr.addAttrib(_var('max_ups',max_ups) )
        self.atr.addAttrib(_var('max_buffer_size',max_buffer_size) )
        self.atr.addAttrib(_var('cycle_buffer',cycle_buffer) )
        self.atr.addAttrib(_var('cmax',cmax) )

    def tree(self):
        tree = ET.Element('qn_method', type=self.type)
        self.atr.fillTree(tree)
        return tree         

class time_stepper():
    def __init__(self,
                 type               : Literal['default'] = 'default',
                 max_retries        : int|bool = 5,
                 opt_iter           : int|bool = 10,
                 dtmin              : float = 0,
                 dtmax              : float = 0.1,
                 aggressiveness     : int|bool = 0,
                 cutback            : float = 0.5,
                 dtforce            : int|bool = 0
                 ):
        
        self.type = type
        self.atr = sectionAttribs()
        self.atr.addAttrib(_var('max_retries',max_retries) )
        self.atr.addAttrib(_var('opt_iter',opt_iter) )
        self.atr.addAttrib(_var('dtmin',dtmin) )
        self.atr.addAttrib(_var('dtmax',dtmax) )
        self.atr.addAttrib(_var('aggressiveness',aggressiveness) )
        self.atr.addAttrib(_var('cutback',cutback) )
        self.atr.addAttrib(_var('dtforce',dtforce) )

    def tree(self):
        tree = ET.Element('time_stepper', type=self.type)
        self.atr.fillTree(tree)
        return tree     

class solver():
    def __init__(self,
                 type                       : Literal['solid'] = 'solid',
                 symmetric_stiffness        : Literal['symmetric'] = 'symmetric',
                 equation_scheme            : Literal['staggered'] = 'staggered',
                 equation_order             : Literal['default'] = 'default',
                 optimize_bw                : int|bool = 0,
                 lstol                      : float|str = 0.9,
                 lsmin                      : float|str = 0.01,
                 lsiter                     : int|str = 5,
                 max_refs                   : int|str = 15,
                 check_zero_diagonal        : int|bool = 0,
                 zero_diagonal_tol          : float|str = 0,
                 force_partition            : int|bool = 0,
                 reform_each_time_step      : int|bool = 1,
                 reform_augment             : int|bool = 0,
                 diverge_reform             : int|bool = 1,
                 min_residual               : float|str = 1E-20,
                 max_residual               : float|str = 0,
                 dtol                       : float|str = 0.001,
                 etol                       : float|str = 0.01,
                 rtol                       : float|str = 0,
                 rhoi                       : float|str = -2,
                 alpha                      : float|str = 1,
                 beta                       : float|str = 0.25,
                 gamma                      : float|str = 0.5,
                 logSolve                   : int|str|bool = 0,
                 arc_length                 : float|str = 0,
                 arc_length_scale           : float|str = 0,
                 qn_method                  : BFGS = BFGS(),
                 ):
        self.type = type
        self.atr = sectionAttribs()
        self.atr.addAttrib(_var('symmetric_stiffness',symmetric_stiffness) )
        self.atr.addAttrib(_var('equation_scheme',equation_scheme) )
        self.atr.addAttrib(_var('equation_order',equation_order) )
        self.atr.addAttrib(_var('optimize_bw',optimize_bw) )
        self.atr.addAttrib(_var('lstol',lstol) )
        self.atr.addAttrib(_var('lsmin',lsmin) )
        self.atr.addAttrib(_var('lsiter',lsiter) )
        self.atr.addAttrib(_var('max_refs',max_refs) )
        self.atr.addAttrib(_var('check_zero_diagonal',check_zero_diagonal) )
        self.atr.addAttrib(_var('zero_diagonal_tol',zero_diagonal_tol) )
        self.atr.addAttrib(_var('force_partition',force_partition) )
        self.atr.addAttrib(_var('reform_each_time_step',reform_each_time_step) )
        self.atr.addAttrib(_var('reform_augment',reform_augment) )
        self.atr.addAttrib(_var('diverge_reform',diverge_reform) )
        self.atr.addAttrib(_var('min_residual',min_residual) )
        self.atr.addAttrib(_var('max_residual',max_residual) )
        self.atr.addAttrib(_var('dtol',dtol) )
        self.atr.addAttrib(_var('etol',etol) )
        self.atr.addAttrib(_var('rtol',rtol) )
        self.atr.addAttrib(_var('rhoi',rhoi) )
        self.atr.addAttrib(_var('alpha',alpha) )
        self.atr.addAttrib(_var('beta',beta) )
        self.atr.addAttrib(_var('gamma',gamma) )
        self.atr.addAttrib(_var('logSolve',logSolve) )
        self.atr.addAttrib(_var('arc_length',arc_length) )
        self.atr.addAttrib(_var('arc_length_scale',arc_length_scale) )
        self.atr.addAttrib(qn_method)

    def tree(self):
        tree = ET.Element('solver', type=self.type)
        self.atr.fillTree(tree)
        return tree        



class Control():
    _opts = Literal[0,1]
    def __init__(self,
                 analysis           : Literal['STATIC', 'DYNAMIC'] = 'STATIC',
                 time_steps         : int|str = 10,
                 step_size          : int|str =0.1,
                 plot_zero_state    : Literal[0, 1] = 0,
                 plot_range         : str = '0,-1',
                 plot_level         : Literal['PLOT_MAJOR_ITRS'] = 'PLOT_MAJOR_ITRS',
                 output_level       : Literal['OUTPUT_MAJOR_ITRS'] = 'OUTPUT_MAJOR_ITRS',
                 plot_stride        : int = 1,
                 adaptor_re_solve   : Literal[0, 1] = 0,
                 time_stepper       : bool|time_stepper = time_stepper(),
                 solver             : solver = solver(),
                 attributes         : dict = {}):
        
        self.type = 'sliding-elastic'
        
        self.atr = sectionAttribs()
        self.atr.addAttrib(_var('analysis',analysis,attributes) )
        self.atr.addAttrib(_var('time_steps',time_steps,attributes) )
        self.atr.addAttrib(_var('step_size',step_size,attributes) )
        self.atr.addAttrib(_var('plot_zero_state',plot_zero_state,attributes) )
        self.atr.addAttrib(_var('plot_range',plot_range,attributes) )
        self.atr.addAttrib(_var('plot_level',plot_level,attributes) )
        self.atr.addAttrib(_var('output_level',output_level,attributes) )
        self.atr.addAttrib(_var('plot_stride',plot_stride,attributes) )
        self.atr.addAttrib(_var('adaptor_re_solve',adaptor_re_solve,attributes) )
        if(time_stepper is not False):
            self.atr.addAttrib(time_stepper)
        self.atr.addAttrib(solver)

    def tree(self):
        tree = ET.Element('Control')
        self.atr.fillTree(tree)
        return tree