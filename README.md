# interFEBio
## a python pre/post processor and fitting API for FEBio 

This repository is based on [siboles/pyFEBio repository](https://github.com/siboles/pyFEBio) and [yskmt/feb-vtl-converter](https://github.com/yskmt/feb-vtk-converter). The main modifications are related to update the writing and reading classes to the latest FEBio xml spec version and xplt binary structure.

The aim of this repository is to support post processing and automated analyses with FEBio, integrating a framework to generate model files (.feb) from a mesh file (just gmsh for now), to read binary files (.xplt) and to run flexible optimization problems with FEBio, using python's LMFIT library.

The implementation does not have all the features of FEBio, however, they will be added in future versions. Additionaly, the implementation could be improved in many ways.

## Documentation
[interFEBio Documentation](https://andresutrera.github.io)


## TODO

- Fix the module type handling. Needs to be load once in the Model class, not per analysis step.
- Add initial section to the pre-process framework.
- Add rigid BC to the boundary class.
- Add linear constraints to the boundary class.
- Generate a Rigid class to handle rigid constrtaints and connections.
- Add all the types of loads to the load class. By now, just nodal loads and pressure are enabled.
- Extend the addContact method to handle more types of inputs (just facet-on-facet is implemented).
- Add a constraint class
- Add discrete class
- Improve the output and logfile handling, allowing to use more flexible types of input/output features of FEBio.
- Improve the MeshData handling to add more features from FEBio (load data from files or xml trees in a more flexible way)

