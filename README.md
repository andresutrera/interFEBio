# interFEBio #
## _a Pre and Post process Python interface for FEBio_
## UNDER DEVELOPMENT ##
## Usage ##
To import the module
<pre><code> import interFEBio </code></pre>

To load a xplt binary:
<pre><code> xpltObj = interFEBio.xplt('Model1.xplt')</code></pre>
<pre><code> xpltObj.readState()</code></pre>
<pre><code> print(xpltObj.listRegions())</code></pre>
<pre><code> print(xpltObj.listSurfaces())</code></pre>
<pre><code> print(xpltObj.listNodesets())</code></pre>

The xplt class contains:

1. xpltObj.dictionary is a dictionary of result variables.
2. xpltObj.time: a list of loaded time steps into the xplt object.
3. 'mesh' class: This class contains the information of the entire mesh, including nodes, elements, surfaces and nodesets.
3.1 xpltObj.mesh.nodes is a [meshNodes, problemDim] array containing the nodal coordinates.
3.2 xpltObj.mesh.domain is a dictionary of domains (materials), with the following structure:
3.2.1 xpltObj.mesh.domain[domainID] = {elemType, nElems, elements = {}}, where elements is a dict of the domain elements.
3.2.1.1 elements[elementID] = {nod1, nod2, ..... , nodN}
3.3 xpltObj.mesh.surface is a dictionary of surfaces with the following structure:
3.3.1 xpltObj.mesh.surface[surfaceID] = {'name', 'nFaces', 'nNodesPerFacet', 'faces' = {}}. Where faces is a dict of the surface faces:
3.3.2 faces[faceID] = {nod1, nod2, ..., nod_nNodesPerFacet}
3.4 xpltObj.mesh.nodeset[nodesetID] = {'name', 'nodeNumber', 'nodes' = []}
3.4.1 nodes is the list of nodes of that nodeset.

4. results variable. This variable is a dictionary that contains the general results of the problem. The structure is:
4.1 xpltObj.results[field][timeStep][region][row][column], where field is the result variable ('displacement', 'stress', 'relative volume', etc). Note that 'Lagrange strain' variable is not a default output in FEBio (FEBioStudio calculate this variable in the post process). TimeStep is the id of the step. region is the region of the mesh (domain) in which you want to obtain a result. For nodal variables, region is always 0. The results are stored in voight notation.

5. a couple of functions can be usted to list and obtain the domain/surfaces/nodesets by name.
5.1 xpltObj.listRegions()
5.2 xpltObj.listSurfaces()
5.3 xpltObj.listNodesets()
5.4 xpltObj.regionID('Material1')
5.5 xpltObj.surfaceID('FacetOnFacetSliding1_primary')
5.6 xpltObj.nodesetID('PrescribedDisplacement1')

## The implementation is still very rudimentary ##
## TODO ##
 1. Improve the overall structure of the xplt class
 2. Implement some additional methods or functions to help the usage of the xplr reader.
