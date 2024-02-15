from setuptools import setup

setup(
    name='interFEBio',
    version='1.0.0',    
    description='Python-FEBio interface',
    url='https://github.com/andresutrera/interfebio',
    author='Andrés Utrera',
    author_email='andres.utrera@usach.cl',
    license='BSD 2-clause',
    packages=['interFEBio'],
    install_requires=['numpy'],

    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
