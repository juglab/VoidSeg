from __future__ import absolute_import
from setuptools import setup, find_packages
from os import path

_dir = path.abspath(path.dirname(__file__))

with open(path.join(_dir,'voidseg','version.py')) as f:
    exec(f.read())

with open(path.join(_dir,'README.md')) as f:
    long_description = f.read()


setup(name='voidseg',
      version=__version__,
      description='VoidSeg is an implementation of 3 class U-Net and StarDist segmentation networks using self-supervised '
                  'Noise2Void denosing for segmentation with limited training data.' 
                  'This implementation extends CARE and uses Noise2Void and StarDist.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/juglab/VoidSeg/',
      author='Mangal Prakash, Tim-Oliver Buchholz, Manan Lalit, Florian Jug, Alexander Krull',
      author_email='prakash@mpi-cbg.de, tibuch@mpi-cbg.de, lalit@mpi-cbg.de, jug@mpi-cbg.de, krull@mpi-cbg.de',
      license='BSD 3-Clause License',
      packages=find_packages(),

      project_urls={
          'Repository': 'https://github.com/juglab/VoidSeg/',
      },

      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'License :: OSI Approved :: BSD License',

          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],

      install_requires=[
	      "n2v",
          "stardist",
	      "numpy",
          "scikit-learn",
          "scipy",
          "matplotlib",
          "six",
          "keras>=2.2.4,<2.3.0",
          "tifffile",
          "tqdm",
          "pathlib2;python_version<'3'",
          "backports.tempfile;python_version<'3.4'",
          "csbdeep>=0.4.0,<0.5.0"
      ]
      )
