'''
Created on 2021-11-22

@author: Andrés Utrera
University of Santiago, Chile
'''
from distutils.core import setup

setup(
    name = 'interFEBio',
    version = '0.1',
    packages = ['interFEBio',],
    py_modules = ['interFEBio.__init__','interFEBio.xplt'],
    author = 'Andrés Utrera',
    author_email = 'andres.utrera@usach.cl',
    license = 'MIT',
    package_data = {'febio': ['examples/*'],},
    #url = 'https://github.com/siboles/pyFEBio',
    #download_url = 'https://github.com/siboles/pyFEBio/tarball/0.1.3',
    description = 'Python interface for FEBio',
    install_requires = [
        "numpy",],
)
