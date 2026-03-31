# ---- This is <test_normprod.py> ----

"""
Test functions implemented in 'normalized_product.normprod'
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

# Define the main data dir
DATA_DIR = pathlib.Path("/g/data/jk72/jl0818/DATA/fast_ice_tests")

# Define your current test site
site = "Thwaites"

# Define loglevel ["DEBUG" or "INFO"]
loglevel = "DEBUG"
loglevel = "INFO"

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

logger.remove()
logger.add(sys.stderr, level=loglevel)

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

# select one image pair to test functions
if len(img_list) == 1:
    logger.warning("Only found one image in GEOTIFF_DIR, cannot test funtions working on image pairs")
    pair = False
else:
    img_pair = img_list[0:2]
    img_pair = [ GEOTIFF_DIR/f for f in img_pair ]
    pair = True

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# -------------------------------------------------- #")
print("# ---------------------- TEST ---------------------  #")
print("# ---- normprod_utils.check_and_trim_image_pair ---- #")
print("# -------------------------------------------------- #\n")

# Get dates as strings
# Testing the 'extract_date' function here
# If this does not work because of changed GA filename structure, the date must be
# extracted from the file names individually
date1 = (normprod_utils.extract_date_from_filename(img_pair[0].stem)).strftime("%Y%m%dT%H%M%S")
date2 = (normprod_utils.extract_date_from_filename(img_pair[1].stem)).strftime("%Y%m%dT%H%M%S")

# Define output_dir
IMG_PAIR_DIR = SITE_DIR / f"S1_image_pair_{date1}_{date2}"

normprod_utils.check_and_trim_image_pair(
    img_pair,
    IMG_PAIR_DIR,
    min_temp_baseline = 11.9,
    max_temp_baseline = 12.1,
    output_epsg = 3031,
    date1 = None,
    date2 = None,
    overwrite = False
)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ------------------------------------ #")
print("# --------------- TEST --------------- #")
print("# ------- normprod.compute_DoB ------- #")
print("# ---- normprod.compute_local_std ---- #")
print("# ------------------------------------ #\n")

# Compute DoB for trimmed georeg files ouput by 'check_and_trim_image_pair'

# Need to find the georeg tif files in IMG_PAIR_DIR
# But do not want to include previously processed DoB or std iamges
exclude_list = ["DoB", "dob", "std"]

# List the georeg files for the IMG_PAIR_DIR
georeg_pair = [
    p for p in IMG_PAIR_DIR.glob("georeg*.tif")
    if not any(excluded in p.name for excluded in exclude_list)
]
georeg_pair.sort(key=lambda p: p.name)


for georeg_path in georeg_pair:

    georeg_basename = georeg_path.stem

    # Define boxcar window width
    w = 11

    # Build path to output dob image
    dob_output_path = IMG_PAIR_DIR / f"{georeg_basename}_window{w}_DoB.tif"

    # Build path to output local_std image
    local_std_output_path = IMG_PAIR_DIR / f"{georeg_basename}_window{w}_local_std.tif"

    logger.debug(f"georeg_basename:       {georeg_basename}")
    logger.debug(f"georeg_path:           {georeg_path}")
    logger.debug(f"dob_output_path:       {dob_output_path}")
    logger.debug(f"local_std_output_path: {local_std_output_path}")

    normprod.compute_DoB(georeg_path, dob_output_path, w)
    normprod.compute_local_std(georeg_path, local_std_output_path, w)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ----------------------------------- #")
print("# --------------- TEST -------------- #")
print("# ---- normprod.compute_normprod ---- #")
print("# ----------------------------------- #\n")

file_list = [p for p in IMG_PAIR_DIR.glob("georeg*.tif")]
file_list.sort(key=lambda p: p.name)

window = 11

dob1 = [f for f in file_list if "georeg_1" in f.name and f"window{window}_DoB" in  f.name][0]
dob2 = [f for f in file_list if "georeg_2" in f.name and f"window{window}_DoB" in  f.name][0]
std1 = [f for f in file_list if "georeg_1" in f.name and f"window{window}_local_std" in  f.name][0]
std2 = [f for f in file_list if "georeg_2" in f.name and f"window{window}_local_std" in  f.name][0]

normprod_smovar_output_path = IMG_PAIR_DIR / f"normprod_smovar_window{window}.tif"

normprod.compute_normprod(dob1, dob2, std1, std2, normprod_smovar_output_path, window, save_intermediate_products=True)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <test_normprod.py> ----
