# normalized_product

Python library for computation of the ___normalized product___ (normprod) for automated mapping of landfast sea ice around Antarctica in Sentinel-1 SAR imagery.
Original development was done in collaboration of ___UiT The Arctic University of Norway___, the ___Universtity of Tasmania___, and ___Geoscience Australia___ as part of the ___Australian Antarctic Program Partnership ([AAPP])___.

## Preparation
This library requires the Geospatial Data Abstraction Layer ([GDAL]) library.
The simplest way to use GDAL with Python is to get the Anaconda Python distribution.
It is recommended to run the code in a virtual environment.
With andaconda, set up the virtual environment like this:

    # create and activate new environment
    conda create -y --name NORMPROD -c conda-forge gdal
    conda activate NORMPROD

    # install requirements
    conda install -y -c conda-forge numpy scipy loguru matplotlib
    pip install ipython



## Installation
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


## Usage
Test scripts and usage examples are provide in the folders test and examples.
Unless you are developing the code further, there is no need to touch the test folder.

The examle folder contains a "quick and dirty" coded example that runs through the entire processing chain for one single image pair.
It provides a subfolder for disributed batch processing which is specifically designed to run on NCI/GADI.

## Batch processing
For full batch processing of a complete test site, you need to adjust __only__ the ___config.yaml___ file in the ___config___ folder.
Your data __must__ be stored according to the folder structure provided below.
The entire batch processing consists of 2 steps:
(1) preprocess_full_test_site.py
(2) batch_process_normprod_smovar.py
Both scripts read the settings from the ___config.yaml___ file and should not require __any__ changes by the user.
All outputs are written to image pair folders within the test site folder.

### Folder Structure
Below is the folder structure for the project:

```
DATA_DIR/
│
├── TestSite1/
│ ├── GA_geotiffs/
│ │ ├── original_GA_intensity_file1.tif    
│ │ ├── original_GA_intensity_file2.tif
│ │ └── ...
│ ├── IMG_PAIR_1/
│ │ ├── georeg_1_*tif
│ │ ├── georeg_1_*tif
│ │ ├── normprod_smovar_window_*tif
│ ├── IMG_PAIR_2/
│ │ ├── georeg_1_*tif
│ │ ├── georeg_1_*tif
│ │ ├── normprod_smovar_window_*tif
│ └── ...
│
├── TestSite2/
│ ├── GA_geotiffs/
│ │ ├── original_GA_intensity_file1.tif    
│ │ ├── original_GA_intensity_file2.tif
│ │ └── ...
│ ├── IMG_PAIR_1/
│ │ ├── georeg_1_*tif
│ │ ├── georeg_1_*tif
│ │ ├── normprod_smovar_window_*tif
│ ├── IMG_PAIR_2/
│ │ ├── georeg_1_*tif
│ │ ├── georeg_1_*tif
│ │ ├── normprod_smovar_window_*tif
│ └── ...
│
└── TestSiteN/
├── GA_geotiffs/
│ │ ├── original_GA_intensity_file1.tif    
│ │ ├── original_GA_intensity_file2.tif
│ └── ...
├── IMG_PAIR_1/
│ │ ├── georeg_1_*tif
│ │ ├── georeg_1_*tif
│ │ ├── normprod_smovar_window_*tif
├── IMG_PAIR_2/
│ │ ├── georeg_1_*tif
│ │ ├── georeg_1_*tif
│ │ ├── normprod_smovar_window_*tif
└── ...
```

- `DATA_DIR/`: The main directory containing all test site subfolders.
- `TestSite1/`, `TestSite2/`, ..., `TestSiteN/`: Subfolders for individual test sites.
- `GA_geotiffs/`: A folder within each test site containing the original GeoTIFF files.
- `IMG_PAIR_1/`, `IMG_PAIR_2/`, ...: Folders for individual image pairs within each test site, containing processed or related files.

[GDAL]: https://gdal.org/
[AAPP]: https://aappartnership.org.au/

