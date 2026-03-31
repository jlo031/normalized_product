# ---- This is <process_full_test_site.py> ----

"""
- Find all S1*tif files for given test site
- Loop over all combinations of image pairs
- If pair meets temporal baseline criteria:
    - Check and trim pair
    - Add IMG_PAIR_DIR to list of valid folders
    - If 'compute_normprod=Tue':
        - compute normprod locally
        - Not recommended if processing many image pairs

User inputs:
main data directory ('DATA_DIR') and a test site ('site').
temporal baseline
output_epsg (almost always 3031 for Antartica)
compute_normprod yes/no
windows (usually 11,21,33)
""" 

import pathlib
from loguru import logger
import sys
import shutil

import math
from itertools import combinations

import numpy as np

from osgeo import gdal

from normalized_product import normprod, normprod_utils

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Set loglevel ["DEBUG" or "INFO"]
loglevel = "DEBUG"
loglevel = "INFO"

logger.remove()
logger.add(sys.stderr, level=loglevel)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# DEFINE AND SET UP DIRECTORY STRUCTURE

# Define the main data dir
DATA_DIR = pathlib.Path("/g/data/jk72/jl0818/DATA/fast_ice_tests")

# Set your current test site
site = "Thwaites_bak"

# Build path site-specific data dir
SITE_DIR =  DATA_DIR / f"{site}"

# Build full path to intensity geotiff dir
GEOTIFF_DIR = SITE_DIR / "GA_geotiffs"

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# DEFINE PROCESSING PARAMETERS

# Temporal baseline
min_temp_baseline = 11.9
max_temp_baseline = 12.1

# Output epsg
output_epsg = 3031

# Overwrite already existing results?
overwrite = False

# Compute the normprod?
# Reccommended to do this in a different process and distribute the jobs
# However, you can do it right here if wanted
compute_normprod = False

# Define window sizes for DoB, local_std, and normprod_smovar
window_list = [11,21,33]

# Save intermediate products during normprod_smovar computation?
save_intermediate_products = False

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# NOTHING TO CHANGE FROM HERE

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

logger.info(f"DATA_DIR:    {DATA_DIR}")
logger.info(f"SITE_DIR:    {SITE_DIR}")
logger.info(f"GEOTIFF_DIR: {GEOTIFF_DIR}")

if not GEOTIFF_DIR.is_dir():
    logger.error(f"Could not find GEOTIFF_DIR: {GEOTIFF_DIR}")

# GEOTIFF_DIR should contain the GA processed geotiff files with backscatter intensity
# List all 'S1*tif' files for current test site
img_list = [ f.name for f in GEOTIFF_DIR.iterdir() if f.name.startswith("S1") and f.name.endswith("tif") ]

logger.info(f"Found {len(img_list)} 'S1*tif' images in GEOTIFF_DIR")

# Report error if not at least two images found
if not any(img_list):
    logger.error("No 'S1*tif' files found in GEOTIFF_DIR")
    sys.exit()

if len(img_list) == 1:
    logger.warning("Only found one image in GEOTIFF_DIR, no pairs available")
    sys.exit()

total_img_pairs = math.comb(len(img_list), 2)
logger.info(f"Total number of img_pairs to process: {total_img_pairs}")

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Loop over all possible image pair combinations

# Initialize a list of image pair folders that match the temporal baseline settings
valid_image_pair_folders = []

for count,img_pair in enumerate(combinations(img_list, 2),1):

    # Convert tuples to pairs (expexted by normprod functions)
    img_pair = list(img_pair)
    logger.info(f"Processing image pair {count}/{total_img_pairs}")
    logger.info(f"img1: {img_pair[0]}")
    logger.info(f"img1: {img_pair[1]}")

    # Add full path to img_pair
    img_pair = [ GEOTIFF_DIR/f for f in img_pair ]

    # Get image datestrings
    # Set these manually from image file names if this fails
    # If you need to do this, then you also need
    date1 = (normprod_utils.extract_date_from_filename(img_pair[0].stem)).strftime("%Y%m%dT%H%M%S")
    date2 = (normprod_utils.extract_date_from_filename(img_pair[1].stem)).strftime("%Y%m%dT%H%M%S")

    # Define IMG_PAIR_DIR
    IMG_PAIR_DIR = SITE_DIR / f"S1_image_pair_{date1}_{date2}"
    ##IMG_PAIR_DIR.mkdir(parents=True, exist_ok=True)

    logger.debug(f"date1: {date1}")
    logger.debug(f"date2: {date2}")
    logger.debug(f"IMG_PAIR_DIR: {IMG_PAIR_DIR}")

    # Check and trim image pair
    valid_pair = normprod_utils.check_and_trim_image_pair(
        img_pair,
        IMG_PAIR_DIR,
        min_temp_baseline = min_temp_baseline,
        max_temp_baseline = max_temp_baseline,
        output_epsg = output_epsg,
        date1 = date1,
        date2 = date2,
        overwrite = overwrite,
    )

    # Add IMG_PAIR_DIR to list if it met the temporal baseline criteria and was succesfully processed
    # If this does not work properly, check the False/True returns from 'normprod_utils.check_and_trim_image_pair'
    if valid_pair:
        valid_image_pair_folders.append(IMG_PAIR_DIR.name)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

    if valid_pair:

        if not compute_normprod:
            logger.info("Not performing actual normprod computation at this point")
            logger.info("You can compute the normprod by setting 'compute_normprod=True'")
            logger.info("For many image pairs, it is recommended to do compute normprod in a separate job")

        else:
            logger.info("Preparing normprod computation")

            normprod.fully_process_single_image_pair(
                IMG_PAIR_DIR,
                windows = window_list,
                save_intermediate_products = save_intermediate_products,
            )


# Write list with valid image pair folders to file for later processing
logger.info("Writing list of valid_image_pair_folders to disk for later processing")

valid_pairs_output_list = SITE_DIR / "valid_img_pair_list.txt"
with open(valid_pairs_output_list, 'w') as f:
    f.write('\n'.join(valid_image_pair_folders) + '\n')
logger.info(f"Successfully wrote {len(valid_image_pair_folders)} entries to {valid_pairs_output_list}")

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <process_full_test_site.py> ----



