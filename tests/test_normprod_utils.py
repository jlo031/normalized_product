# ---- This is <test_normprod_utils.py> ----

"""
Test functions implemented in 'normalized_product.normprod_utils'
""" 

import pathlib
from loguru import logger

import numpy as np

from osgeo import gdal

from normalized_product import normprod_utils

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Define the main data dir
DATA_DIR = pathlib.Path("/g/data/jk72/jl0818/DATA/fast_ice_tests")

# Define your current test site
site = "Thwaites"

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Build path site-specific data dir
SITE_DIR =  DATA_DIR / f"{site}"

# Build full path to intensity geotiff dir
GEOTIFF_DIR = SITE_DIR / "GA_geotiffs"

logger.debug(f"DATA_DIR:    {DATA_DIR}")
logger.debug(f"SITE_DIR:    {SITE_DIR}")
logger.debug(f"GEOTIFF_DIR: {GEOTIFF_DIR}")

if not GEOTIFF_DIR.is_dir():
    logger.error(f"Could not find GEOTIFF_DIR: {GEOTIFF_DIR}")


# Hard-code image pair (located in GEOTIFF_DIR
image_pair = [
    "S1A__EW___A_20240906T042826_HH_grd_mli_gamma0-rtc_geo_db_3031.tif",
    "S1A__EW___A_20240918T042826_HH_grd_mli_gamma0-rtc_geo_db_3031.tif"
]

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ------------------------------------------- #")
print("# ------------------- TEST ------------------ #")
print("# ---- normprod_utils.check_raster_stats ---- #")
print("# ------------------------------------------- #\n")

for img_file in image_pair:

    img_path = GEOTIFF_DIR / img_file
    logger.debug(f"img_path: {img_path}")

    if not img_path.is_file():
        logger.error(f"Could not find img_path: {img_path}")
    else:
        normprod_utils.check_raster_stats(img_path)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ----------------------------------- #")
print("# --------------- TEST -------------- #")
print("# ---- normprod_utils.fill_nans ----  #")
print("# ----------------------------------- #\n")

# Load both images
img1 = gdal.Open(GEOTIFF_DIR/image_pair[0]).ReadAsArray()
img2 = gdal.Open(GEOTIFF_DIR/image_pair[1]).ReadAsArray()

# Find all nan indices in both images
img1_nan_idx = np.where(np.isnan(img1))
img2_nan_idx = np.where(np.isnan(img2))

logger.info(f"img1 has {len(img1_nan_idx[0])} nan values")
logger.info(f"img2 has {len(img2_nan_idx[0])} nan values")

img1_filled = normprod_utils.fill_nans(img1)
img2_filled = normprod_utils.fill_nans(img2)

# Find all nan indices in both images after filling (should be 0)
img1_filled_nan_idx = np.where(np.isnan(img1_filled))
img2_filled_nan_idx = np.where(np.isnan(img2_filled))

logger.info(f"img1_filled has {len(img1_filled_nan_idx[0])} nan values")
logger.info(f"img2_filled has {len(img2_filled_nan_idx[0])} nan values")


# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <test_normprod_utils.py> ----
