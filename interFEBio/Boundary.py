"""
This module deals with boundary conditions (Fixed, prescribed, contact)

# TODO

 - Enable spring BC (check spec 3.0 format)
 - Enable contact default parameters for majority of the methods (is just implemented for sliding-facet-on-facet)

"""
from __future__ import print_function
from builtins import range
from builtins import object


class Boundary(object):
    '''
    Class for assign boundary conditions
    '''

    def __init__(self,steps=1):
        """
        Create a list of BC containing a dictionary with the different types at each step.

        Args:
        ----------

            steps: Number of steps for the BC list.

        """
        self.bcs = []
        for _ in range(steps+1):
            self.bcs.append({'fixed': [], 'prescribed': [], 'prescribed relative': [], 'contact': [],'spring': []})

    def addFixed(self,step=0,nset=None,nodeid=None,dof=None):
        """

        Add a fixed BC to a nodeset or nodeid (as list of nodes or single node integer).
        The fixed dofs needs to be comma separated (e.g. 'x,y,z').
        The default step for fixed BC is 0 (that means a permanent BC in the entire FE analysis).

        Args
        ----------

            step (int): step at which the BC will be applied.

            nset (str): Nodeset which will be fixed.

            nodeid (int/list): Node id or list of node ids to be Fixed.

            dof (str): Degree/s of freedom to be fixed. Comma separated ('x,y,z')

        Example
        ----------
        >>> addFixed(step=1, nset='bottomFace', dof='z')

        """
        if dof is None:#: Instance variable's doc-comment
            print('WARNING: No degree of freedom was specified for this boundary condition.  Skipping...')
            pass

        if nset is None and nodeid is None:
            print('WARNING: Must specify either a node set or a node id.  Skipping...')
            pass

        if nset is not None:
            #print(nset)
            #for n in nset:
            #    self.bcs[0]['fixed'].append([n,dof])
            self.bcs[0]['fixed'].append(['nodeset',nset,dof])

        if nodeid is not None:
            if isinstance(nodeid, list):
                for n in nodeid:
                    self.bcs[0]['fixed'].append(['node',str(n),dof])
            else:
                self.bcs[0]['fixed'].append(['node',str(nodeid),dof])


    def addPrescribed(self,nset=None,step=0,nodeid=None,dof=None,lc=None,scale=None,ptype='prescribed'):
        """

        Add a prescribed BC to a nodeset or nodeid (as list of nodes or single node integer).
        The default step for prescribed BC is 0 (that means a permanent BC in the entire FE analysis).

        Args
        ----------

            step (int): step at which the BC will be applied.

            nset (str): Nodeset which will be fixed.

            nodeid (int/list): Node id or list of node ids to be Fixed.

            dof (str): Degree/s of freedom to be fixed. Single axis.

            lc (str): Load controller id.

            scale (float): Scale to be applied in the BC

            ptype (str): 'prescribed'/'prescribed relative' identifier.

        Example
        ----------
        >>> addPrescribed(step=1, nset='bottomFace', dof='z', lc='1', scale=2, ptype='prescribed relative')

        """
        if dof is None:
            print('WARNING: No degree of freedom was specified for this boundary condition.  Skipping BC assignment...')
            pass

        if nset is None and nodeid is None:
            print('WARNING: Must specify either a node set or a node id.  Skipping BC assignment...')
            pass

        if lc is None:
            print('WARNING: Must specify a load curve ID. Skipping BC assignment...')
            pass

        if scale is None:
            print('WARNING: No scale specified for this boundary condition.  Using default of 1.0...')
            scale = 1.0


        if nset is not None:
            self.bcs[step][ptype].append(['nodeset',nset,dof,lc,scale])

        if nodeid is not None:
            if isinstance(nodeid, list):
                for n in nodeid:
                    self.bcs[step][ptype].append(['node',str(n),dof,lc,scale])
            else:
                self.bcs[step][ptype].append(['node',str(nodeid),dof,lc,scale])

    def addContact(self,step=0,ctype=None,master=None,slave=None,attributes=None):
        """

        Add a contact interface between two surfaces.

        Args
        ----------

            step (int): step at which the BC will be applied.

            ctype (str): Contact type.
                sliding-node-on-facet
                sliding-facet-on-facet
                sliding-elastic
                sliding-biphasic
                sliding-biphasic-solute
                sliding-multiphasic
                rigid_wall
                rigid_joint
                tied
                sticky
                tied-biphasic

            master (str): Master surface name.

            slave (str): Slave surface name.

            attributes (dict): Dictionary of attributes.


        Example
        ----------
        >>> addContact(step=1,ctype='sliding-facet-on-facet',master="top",slave="contact",attributes={'auto_penalty' : 1, 'update_penalty' : 1})

        """
        if ctype is None:
            print('WARNING: Did not specify a contact type. Skipping assignment...')
            pass

        elif master is None or slave is None:
            print('WARNING: Did not specify an appropriate value for the master and/or slave.  Skipping assignment...')
            pass
        try:
            if isinstance(master[0][0],list):
                dmy = []
                for i in master:
                    for j in i:
                        dmy.append(j)
                master = dmy
        except:
            master = master
        try:
            if isinstance(slave[0][0],list):
                dmy = []
                for i in slave:
                    for j in i:
                        dmy.append(j)
                slave = dmy
        except:
            slave = slave
        self.bcs[step]['contact'].append({'type': ctype, 'master': master, 'slave': slave, 'attributes': attributes})

    #Springs not verified yet.
    # def addSpring(self,step=0,stype='linear',nodes=[None,None],E=None,lc=None,scale=1.0):
    #     if len(nodes) != 2 or not isinstance(nodes[0],int) or not isinstance(nodes[1],int):
    #         print('WARNING: List of nodes must be 2 integer elements.  Skipping spring definition...')
    #         pass
    #     if stype=='linear' or stype=='tension-only nonlinear':
    #         if E is None:
    #             print('WARNING: Must specify a spring stiffness if type is linear or tension-only linear.  Skipping spring definition...')
    #             pass
    #     if stype=='nonlinear' and lc is None:
    #         print('WARNING: Must specify a force load curve if type is nonlinear.  Skipping spring definition...')
    #         pass
    #     if stype=='nonlinear' and scale is None:
    #         print('WARNING: No scale was specified.  Using default value of 1.0...')
    #         scale = 1.0
    #
    #     self.bcs[step]['spring'].append({'stype':stype,'n1':nodes[0],'n2':nodes[1],'E':E,'lc':lc,'scale':scale})
