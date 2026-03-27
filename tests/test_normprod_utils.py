# ---- This is <test_normprod_utils.py> ----

"""
Test functions implemented in 'normalized_product.normprod_utils'.
""" 

import pathlib
from loguru import logger
import sys
import shutil

import numpy as np

from osgeo import gdal

from normalized_product import normprod_utils

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Define the main data dir
DATA_DIR = pathlib.Path("/g/data/jk72/jl0818/DATA/fast_ice_tests")

# Define a test site
site = "Thwaites"

# Define loglevel ["DEBUG" or "INFO"]
loglevel = "DEBUG"
##loglevel = "INFO"

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
else:
    n_img = len(img_list)
    logger.info(f"Found {n_img} 'S1*tif' images in GEOTIFF_DIR")

# Select one single image to test functions
img_path = GEOTIFF_DIR / img_list[0]
logger.debug(f"img_path: {img_path}")

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
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ------------------------------------------- #")
print("# ------------------- TEST ------------------ #")
print("# ---- normprod_utils.check_raster_stats ---- #")
print("# ------------------------------------------- #\n")

normprod_utils.check_raster_stats(img_path)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ----------------------------------- #")
print("# --------------- TEST -------------- #")
print("# ---- normprod_utils.fill_nans ----  #")
print("# ----------------------------------- #\n")

# Load image
img = gdal.Open(img_path).ReadAsArray()

# Find all nan indices in both images
img_nan_idx = np.where(np.isnan(img))

# Fill image nans
img_filled = normprod_utils.fill_nans(img)

# Find all nan indices in both images after filling (should be 0)
img_filled_nan_idx = np.where(np.isnan(img_filled))

logger.info(f"img has {len(img_nan_idx[0])} nan values")
logger.info(f"img_filled has {len(img_filled_nan_idx[0])} nan values")

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ---------------------------------------------- #")
print("# -------------------- TEST -------------------- #")
print("# ---- normprod_utils.nan_safe_mean_filter ----  #")
print("# ---------------------------------------------- #\n")

img_mean = normprod_utils.nan_safe_mean_filter(img)
img_filled_mean = np.mean(img_filled)

logger.info(f"nan_safe_mean og img:  {img_mean}")
logger.info(f"np.mean of img_filled: {img_filled_mean}")

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ------------------------------------------------------ #")
print("# ------------------------ TEST ------------------------ #")
print("# ----- normprod_utils.extract_date_from_filename -----  #")
print("# ---- normprod_utils.extract_date_from_datestring ----  #")
print("# ------------------------------------------------------ #\n")

filename = img_path.name
random_test_datestring = "19860511T023000"

date_from_filename = normprod_utils.extract_date_from_filename(filename)
date_from_datestring = normprod_utils.extract_date_from_datestring(random_test_datestring)

logger.debug(f"filename: {filename}")
logger.debug(f"random_test_datestring: {random_test_datestring}")

logger.info(f"date from filename: {date_from_filename}")
logger.info(f"date from datestring: {date_from_datestring}")

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# ---------------------------------------------- #")
print("# -------------------- TEST -------------------- #")
print("# ---- normprod_utils.get_valid_data_extent ---- #")
print("# ---------------------------------------------- #\n")

# Open GDAL data set
ds = gdal.Open(img_path)

extent = normprod_utils.get_valid_data_extent(ds)

ds = None

logger.info(f"Extracted data extent: {extent}")

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

print("\n# -------------------------------------------------- #")
print("# ---------------------- TEST ---------------------- #")
print("# ---- normprod_utils.check_and_trim_image_pair ---- #")
print("# -------------------------------------------------- #\n")

if not pair:
    logger.warning("Only found one image in GEOTIFF_DIR, cannot test funtions working on image pairs")
else:

    output_dir = pathlib.Path("./tmp_outputs").resolve()
    if output_dir.is_dir():
        shutil.rmtree(output_dir)

    normprod_utils.check_and_trim_image_pair(
        img_pair,
        output_dir,
        min_temp_baseline = 11.9,
        max_temp_baseline = 12.1,
        output_epsg = 3031,
        date1 = None,
        date2 = None,
        overwrite = False
    )

    georeg_files = [ f for f in output_dir.iterdir() ]

    logger.info(f"Trimmed image pair files written to: {output_dir}")
    logger.info(f"georeg_files: {georeg_files}")


    # Check outputs
    if len(georeg_files)!=2:
        logger.error(f"output_dir should have exactly 2 files now, but has {len(georeg_files)}")
    else:
        ds1 = gdal.Open(georeg_files[0])
        ds2 = gdal.Open(georeg_files[1])


        # Get (Width, Height)
        dim1 = (ds1.RasterXSize, ds1.RasterYSize)
        dim2 = (ds2.RasterXSize, ds2.RasterYSize)

        if dim1 == dim2:
            logger.info(f"Dimensions match: {dim1}")
        else:
            logger.error(f"Dimensions differ: {dim1} vs {dim2}")

        # Get geotransform
        gt1 = ds1.GetGeoTransform()
        gt2 = ds2.GetGeoTransform()

        if gt1 == gt2:
            logger.info(f"Geotransforms match: {gt1}")
        else:
            logger.error(f"Geotransforms differ: {gt1} vs {gt2}")

    # Clean up
    ds = ds1 = d2 = None
    gdal.GDALDestroyDriverManager() 
    gdal.AllRegister()
    if output_dir.is_dir():
        try:
            shutil.rmtree(output_dir)
        except OSError:
            logger.warning("Cannot cleanup 'output_dir'")

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# ---- End of <test_normprod_utils.py> ----
