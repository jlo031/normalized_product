# ---- This is <process_single_img_pair.py> ----

"""
Fully process a single image pair:
    - List all images in GEOTIFF_DIR
    - Select first two images as img_pair
    - Pre-process img_pair: normprod_utils.check_and_trim_image_pair
    - Comnpute DoB, local std, normprod_smovar: normprod.fully_process_single_image_pair(
""" 

import pathlib
from loguru import logger
import sys
import shutil

import numpy as np

from osgeo import gdal

from normalized_product import normprod, normprod_utils

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Define loglevel ["DEBUG" or "INFO"]
loglevel = "DEBUG"
##loglevel = "INFO"

logger.remove()
logger.add(sys.stderr, level=loglevel)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Define the main data dir
DATA_DIR = pathlib.Path("/g/data/jk72/jl0818/DATA/fast_ice_tests")

# Define your current test site
site = "Thwaites"

# Build path site-specific data dir
SITE_DIR =  DATA_DIR / f"{site}"

# Build full path to intensity geotiff dir
GEOTIFF_DIR = SITE_DIR / "GA_geotiffs"

logger.debug(f"DATA_DIR:    {DATA_DIR}")
logger.debug(f"SITE_DIR:    {SITE_DIR}")
logger.debug(f"GEOTIFF_DIR: {GEOTIFF_DIR}")

if not GEOTIFF_DIR.is_dir():
    logger.error(f"Could not find GEOTIFF_DIR: {GEOTIFF_DIR}")

# Find all S1 tif files in GEOTIFF_DIR
img_list = [ f.name for f in GEOTIFF_DIR.iterdir() if f.name.startswith("S1") and f.name.endswith("tif") ]

if not any(img_list):
    logger.error("No 'S1*tif' files found in GEOTIFF_DIR")
    pair = False
    sys.exit()

# select one image pair to test functions
if len(img_list) == 1:
    logger.warning("Only found one image in GEOTIFF_DIR, cannot test funtions working on image pairs")
    pair = False
    sys.exit()
else:
    img_pair = img_list[0:2]
    img_pair = [ GEOTIFF_DIR/f for f in img_pair ]
    pair = True

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Get image datestrings (set manual/from image pair if this fails due to changed file name
date1 = (normprod_utils.extract_date_from_filename(img_pair[0].stem)).strftime("%Y%m%dT%H%M%S")
date2 = (normprod_utils.extract_date_from_filename(img_pair[1].stem)).strftime("%Y%m%dT%H%M%S")

# Define output_dir
IMG_PAIR_DIR = SITE_DIR / f"S1_image_pair_{date1}_{date2}"

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Temporal baseline
min_temp_baseline = 11.9
max_temp_baseline = 12.1

# Output epsg
output_epsg = 3031

normprod_utils.check_and_trim_image_pair(
    img_pair,
    IMG_PAIR_DIR,
    min_temp_baseline = min_temp_baseline,
    max_temp_baseline = max_temp_baseline,
    output_epsg = output_epsg,
    date1 = None,
    date2 = None,
    overwrite = False,
)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Define window sizes to process
window_list = [11,21,33]

normprod.fully_process_single_image_pair(
    IMG_PAIR_DIR,
    windows = window_list,
    save_intermediate_products = False,
)
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <process_single_img_pair.py> ----



