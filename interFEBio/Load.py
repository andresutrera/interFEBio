"""
This module handles the load section for each step.

# TODO

 - Check for solute-flux, fluid-flux, traction and body-force. Disabled for now

"""
from __future__ import print_function
from builtins import range
from builtins import object

class Load(object):
    '''
    Load class to assign loads at each time interval.
    Create a list of loads containing a dictionary with the different types of load for each interval.

    Args:
    ----------

        steps(int): Number of steps for the load list.
    '''

    def __init__(self,steps=1):
        '''
        Constructor
        '''
        self.loads = []
        for _ in range(steps):
            self.loads.append({'force': [], 'pressure': [], 'normal_traction': [], 'fluidflux': [], 'soluteflux': [], 'body_force': []})

    def addForce(self,step=0,nset=None,nodeid=None,dof=None,lc=None,scale=None):
        """

        Add a force load to a nodeset or nodeid (as list of nodes or single node integer).
        The default step for this load is 0 (that means a permanent load in the entire FE analysis).

        Args
        ----------

            step (int): step at which the BC will be applied.

            nset (str): Nodeset which will be fixed.

            nodeid (int/list): Node id or list of node ids to be Fixed.

            dof (str): Degree/s of freedom to be fixed. Comma separated ('x,y,z')

            lc (str): Load controller id.

            scale (float): Scale to be applied in the load

        Example
        ----------
        >>> addLoad(step=1, nset='topFace', dof='z', lc='1', scale='1.0')

        """
        if dof is None:
            print('WARNING: No degree of freedom was specified for this nodal force.  Skipping assignment...')
            pass

        if nset is None and nodeid is None:
            print('WARNING: Must specify either a node set or a node id.  Skipping BC assignment...')
            pass

        if lc is None:
            print('WARNING: No load curve ID specified for nodal force. Assuming load curve ID of 1...')
            pass

        if scale is None:
            print('WARNING: No scale specified for nodal force.  Using default of 1.0...')
            scale = '1.0'

        if nset is not None:
            for n in nset:
                self.loads[step]['force'].append([n,dof,lc,scale])

        if nodeid is not None:
            if isinstance(nodeid, list):
                for n in nodeid:
                    self.loads[step]['force'].append([n,dof,lc,scale])
            else:
                self.loads[step]['force'].append([nodeid,dof,lc,scale])

    def addPressure(self,step=0,surface=None,lc=None,pressure=None,linear=True,symmetric=True,shellBottom = False):
        """

        Add a pressure load to a given surface.
        The default step for this load is 0 (that means a permanent load in the entire FE analysis).

        Args
        ----------

            step (int): step at which the BC will be applied.

            surface (str): Surface to apply the pressure load.

            lc (str): Load controller id.

            pressure (float): Pressure to be applied.

            linear (bool): linear formulation. default is linear

            symmetric (bool): Symmetric formualtion. Default is symmetric.

            shellBottom (bool): Apply pressure at shell bottom. Default is Disabled

        Example
        ----------
        >>> addPressure(step=1, nset='pressureFace',lc='1', pressure='10E-3')

        """
        if surface is None:
            print('WARNING: Must specify surface as a MeshDef.fset object. Skipping pressure assignment...')
            pass
        if lc is None:
            print('WARNING: No load curve ID specified for pressure.  Assuming load curve ID of 1...')
            lc = '1'
        if pressure is None:
            print('WARNING: No scale factor specified for pressure.  Assuming pressure factor of 1.0...')
            pressure = '1.0'


        self.loads[step]['pressure'].append({'lc': lc, 'pressure': pressure, 'surface': surface, 'linear' : linear, 'symmetric' : symmetric, 'shellBottom' : shellBottom})


    #
    # def addTraction(self,step=0,surface=None,traction=None,lc=None,scale=None):
    #     if surface is None:
    #         print('WARNING: Must specify surface as a MeshDef.fset object. Skipping prescribed traction assignment...')
    #         pass
    #     if traction is None:
    #         print('WARNING: No traction type specified.  Assuming "mixture"...')
    #         traction = 'mixture'
    #     if lc is None:
    #         print('WARNING: No load curve ID specified for prescribed traction. Assuming load curve ID of 1...')
    #         lc = '1'
    #     if scale is None:
    #         print('WARNING: No scale factor specified for prescribed traction.  Assuming scale factor of 1.0...')
    #         scale = '1.0'
    #
    #     self.loads[step]['normal_traction'].append({'traction': traction,'lc': lc, 'scale': scale, 'surface': surface})
    #
    # def addFluidFlux(self,step=0,method=None,surface=None,fluxtype=None,lc=None,scale=None):
    #     if method is None:
    #         print('WARNING: No method specified for flux condition. Assuming to be "nonlinear"...')
    #         method = 'nonlinear'
    #     if surface is None:
    #         print('WARNING: Must specify surface as a MeshDef.fset object. Skipping flux condition assignment...')
    #         pass
    #     if fluxtype is None:
    #         print('WARNING: No fluxtype was specified.  Assuming to be "fluid"')
    #         fluxtype = 'fluid'
    #     if lc is None:
    #         print('WARNING: No load curve specified for flux condition. Assuming load curve as 1...')
    #         lc = '1'
    #     if scale is None:
    #         print('WARNING: No scale factor specified for flux condition. Assuming scale factor as 1.0...')
    #         scale = '1.0'
    #
    #     self.loads[step]['fluidflux'].append({'type': method, 'flux': fluxtype, 'lc': lc, 'scale': scale, 'surface': surface})
    #
    # def addSoluteFlux(self,step=0,method=None,surface=None,solute=None,lc=None,scale=None):
    #     if method is None:
    #         print('WARNING: No method specified for flux condition. Assuming to be "nonlinear"...')
    #         method = 'nonlinear'
    #     if surface is None:
    #         print('WARNING: Must specify surface as a MeshDef.fset object. Skipping flux condition assignment...')
    #         pass
    #     if lc is None:
    #         print('WARNING: No load curve specified for flux condition. Assuming load curve as 1...')
    #         lc = '1'
    #     if scale is None:
    #         print('WARNING: No scale factor specified for flux condition. Assuming scale factir as 1.0...')
    #         scale = '1.0'
    #     self.loads[step]['fluidflux'].append({'type': method, 'sol': solute, 'lc': lc, 'scale': scale, 'surface': surface})
    #
    # def addBodyForce(self,step=0,btype=None,attributes=None):
    #     if btype is None:
    #         print("WARNING: Must specify a body force type.  Skipping assignment...")
    #         pass
    #     if attributes is None:
    #         print("WARNING: No attributes specified for body force.  Skipping assignment...")
    #         pass
    #
    #     self.loads[step]['body_force'].append({'type': btype, 'attributes': attributes})
