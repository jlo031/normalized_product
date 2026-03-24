# normalized_product

Library for computation of normalized product (normprod), developed for automated mapping of landfast sea ice around Antarctica in Sentinel-1 SAR imagery.

### Preparation
This library requires the Geospatial Data Abstraction Layer ([GDAL]) library.
The simplest way to use GDAL with Python is to get the Anaconda Python distribution.
It is recommended to run the code in a virtual environment.
With andaconda, set up the virtual environment like this:

    # create and activate new environment
    conda create -y --name NORMPROD -c conda-forge gdal
    conda activate NORMPROD

    # install requirements
    conda install -y - conda-forge numpy scipy loguru matplotlib datetime
    pip install ipython



### Installation
You can install this library directly from github (1) or locally after cloning (2).  

1. **Installation from github**

       # install this package
       pip install git+https://github.com/jlo031/normalized_product

2. **Local installation**

       # clone the repository
       git clone git@github.com:jlo031/normalized_product

   Change into the main directory of the cloned repository (it should contain the *setup.py* file) and install the library:

       # installation
       pip install .


### Usage
Test scripts and usage examples are provide in the folders test and examples.






[GDAL]: https://gdal.org/
