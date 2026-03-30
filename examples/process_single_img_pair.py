# ---- This is <process_single_img_pair.py> ----

"""
Process a single image pair, compute normprod for 3 distinct window sizes.
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
loglevel = "INFO"

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

# DEFINE ALL PROCESSING PARAMETERS

# Image pair
img_pair = [
    GEOTIFF_DIR / img_list[0],
    GEOTIFF_DIR / img_list[1]
]

# Get image datestrings (set manual/from image pair if this fails due to changed file name
date1 = (normprod_utils.extract_date_from_filename(img_pair[0].stem)).strftime("%Y%m%dT%H%M%S")
date2 = (normprod_utils.extract_date_from_filename(img_pair[1].stem)).strftime("%Y%m%dT%H%M%S")

# Define output_dir
IMG_PAIR_DIR = SITE_DIR / f"S1_image_pair_{date1}_{date2}"

# temporal baseline
min_temp_baseline = 11.9
max_temp_baseline = 12.1

# output epsg
output_epsg = 3031

# overwrite existing results
overwrite = False

# Define window sizes to process
window_list = [11,21,33]




# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

img_pair = 



def process_single_pair(img_pair, img_pair_dir, min_temp_baseline)







































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











"""
import matplotlib.pyplot as plt

from scipy.ndimage import uniform_filter



# THIS IS FROM BOXCAR DIFFERENCE

image_path1 = GEOTIFF_DIR / image_pair[0]

width = 11

ds1 = gdal.Open(image_path1, gdal.GA_ReadOnly)
band1 = ds1.GetRasterBand(1).ReadAsArray()
band_filled1 = normprod_utils.fill_nans(band1)
smoothed1 = uniform_filter(band_filled1, size=width, mode="nearest")
diff1 = band1 - smoothed1


# NOW ADD LOCAL STD STUFF

local_mean1 = uniform_filter(band_filled1, size=width, mode="nearest")
local_mean_sq1 = uniform_filter(band_filled1**2, size=width, mode="nearest")

local_std1 = np.sqrt(local_mean_sq1 - local_mean1**2)




# THIS IS FROM BOXCAR DIFFERENCE

image_path2 = GEOTIFF_DIR / image_pair[1]
width = 11

ds2 = gdal.Open(image_path2, gdal.GA_ReadOnly)
band2 = ds2.GetRasterBand(1).ReadAsArray()
band_filled2 = normprod_utils.fill_nans(band2)
smoothed2 = uniform_filter(band_filled2, size=width, mode="nearest")
diff2 = band2 - smoothed2

# NOW ADD LOCAL STD STUFF

local_mean2 = uniform_filter(band_filled2, size=width, mode="nearest")
local_mean_sq2 = uniform_filter(band_filled2**2, size=width, mode="nearest")

local_std2 = np.sqrt(local_mean_sq2 - local_mean2**2)





sub = 5
fig, axes = plt.subplots(2,4,sharex=True,sharey=True, figsize=((20,14)))
axes = axes.ravel()

x1=5000
x2=8000
y1=7000
y2=10000

axes[0].imshow(band1[x1:x2,y1:y2], cmap="gray", vmin=-20, vmax=0)
axes[1].imshow(band_filled1[x1:x2,y1:y2], cmap="gray", vmin=-20, vmax=0)
axes[2].imshow(smoothed1[x1:x2,y1:y2], cmap="gray", vmin=-20, vmax=0)
axes[3].imshow(diff1[x1:x2,y1:y2], cmap="gray", vmin=-3, vmax=3)

axes[4].imshow(band2[x1:x2,y1:y2], cmap="gray", vmin=-20, vmax=0)
axes[5].imshow(band_filled2[x1:x2,y1:y2], cmap="gray", vmin=-20, vmax=0)
axes[6].imshow(smoothed2[x1:x2,y1:y2], cmap="gray", vmin=-20, vmax=0)
axes[7].imshow(diff2[x1:x2,y1:y2], cmap="gray", vmin=-3, vmax=3)

axes[0].set_title("Img1 HH")
axes[1].set_title("Img1 HH filled")
axes[2].set_title("Img1 HH smoothed")
axes[3].set_title("Img1 HH DoB")

axes[4].set_title("Img2 HH")
axes[5].set_title("Img2 HH filled")
axes[6].set_title("Img2 HH smoothed")
axes[7].set_title("Img2 HH DoB")

plt.show()

















# Test Gabby's image pair finding and region selection

import os
from osgeo import osr

localDataDir = GEOTIFF_DIR


# List all GA geotiff files in the current data dir
full_filenames = sorted([f for f in localDataDir.iterdir() if f.is_file() and "S1" in f.name])

# Get all the file names
base_filenames = [f.name for f in full_filenames]





##################################

# THIS ENTIRE CELL IS APPARENTLY NOT NEEDED


# Use all image pair combinations from file list
useRange = range(len(base_filenames))


# ???
startXs = []
endXs = []
deltaXs = []
startYs = []
endYs = []
deltaYs = []


# Want to find common bounds for whole stack.
for which in useRange:
    print(which)
    geoGRDi = os.path.join(localDataDir, base_filenames[which])  ### THIS SEEMS STRANGE. COULD JUST USE THE full_filenames
    print(geoGRDi)
    if os.path.exists(geoGRDi):
        #check extents overlap and crop to intersection with gdal.Warp
        DSi = gdal.Open(geoGRDi, gdal.GA_ReadOnly)
        NXi, NYi, NBi = DSi.RasterXSize, DSi.RasterYSize, DSi.RasterCount
        geoti = DSi.GetGeoTransform()
        startXs.append(geoti[0])
        endXs.append(geoti[0]+geoti[1]*NXi)
        startYs.append(geoti[3])
        endYs.append(geoti[3]+geoti[5]*NYi)  # NB. geoti[5] is -ve.
        deltaXs.append(geoti[1])
        deltaYs.append(geoti[5])
        geoti = None
        DSi = None
	
##################################


allPairs = []  # Store valid pairs

outputEPSG = 3031
Psrs = osr.SpatialReference()
Psrs.ImportFromEPSG(outputEPSG)

# Iterate over all unique image pairs
for i in range(len(base_filenames)):
    for j in range(i + 1, len(base_filenames)):

        base1 = base_filenames[i]
        base2 = base_filenames[j]
        
        logger.info("Processing image pair:")
        logger.info(f"    {base1}")
        logger.info(f"    {base2}")

        date1 = extract_date(base1)
        date2 = extract_date(base2)

        # Calcualte temporal baseline in days
        temp_baseline_days = np.abs((date1 - date2).days)

        logger.info(f"    date1: {date1}")
        logger.info(f"    date2: {date2}")
        logger.info(f"    temporal baseline in days: {temp_baseline_days}")


        allPairs.append([i, j])  # Store valid pair indices
 
        # CAN USE THE FULL FILENAMES INSTEAD HERE, NO NEED TO STITCH TOGETHER AGAIN
        geoGRD1 = os.path.join(localDataDir, base1)
        geoGRD2 = os.path.join(localDataDir, base2)


        # Make an output folder for this image pair
        compareFold = os.path.join(localDataDir, f"ISCE3_NormProd_EW_{date1.strftime('%Y%m%d')}_{date2.strftime('%Y%m%d')}")
        os.makedirs(compareFold, exist_ok=True)


        # Open data sets
        DS1 = gdal.Open(geoGRD1, gdal.GA_ReadOnly)
        DS2 = gdal.Open(geoGRD2, gdal.GA_ReadOnly)
            
        georeg1 = os.path.join(compareFold, f"georeg_1_{date1.strftime('%Y%m%d')}_EPSG{outputEPSG}.tif")
        georeg2 = os.path.join(compareFold, f"georeg_2_{date2.strftime('%Y%m%d')}_EPSG{outputEPSG}.tif")
        justMade = False

        extent1 = get_valid_data_extent(DS1)
        extent2 = get_valid_data_extent(DS2)




        # Compute the INTERSECTION of the extents
        if extent1 and extent2:
            min_x = max(extent1[0], extent2[0])  # Max of min_x
            min_y = max(extent1[1], extent2[1])  # Max of min_y
            max_x = min(extent1[2], extent2[2])  # Min of max_x
            max_y = min(extent1[3], extent2[3])  # Min of max_y
            xRes = min(extent1[4], extent2[4])  # Use the finer resolution
            yRes = min(extent1[5], extent2[5])  

               
            # Check if valid intersection exists
            if min_x >= max_x or min_y >= max_y:
                print(f"\u274c No overlapping region between {base1} and {base2}. Skipping.")
                continue
        else:
            print(f"\u274c One of the images is fully NaN. Skipping.")
            continue




        if not (os.path.exists(georeg1) and os.path.exists(georeg2)):
            gdal.Warp(georeg1, DS1, format="GTiff", dstSRS=Psrs, outputBounds=(min_x, min_y, max_x, max_y), 
                      xRes=xRes, yRes=yRes, dstNodata=np.nan, 
                      outputType=gdal.GDT_Float32, creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
            gdal.Warp(georeg2, DS2, format="GTiff", dstSRS=Psrs, outputBounds=(min_x, min_y, max_x, max_y), 
                      xRes=xRes, yRes=yRes, dstNodata=np.nan, 
                      outputType=gdal.GDT_Float32, creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
            justMade = True




## IMPLEMENTING THIS ALL AS A FUNCTION IN normprod_util WORKIN ON ONE IMAGE PAIR ##


img_pair = [
    GEOTIFF_DIR / image_pair[0],
    GEOTIFF_DIR / image_pair[1]
]


check_and_trim_image_pair(
    img_pair,
    "test"
)


allPairs = []  # Store valid pairs
threshold_min = 11.9
threshold_max = 12.1



outputEPSG = 3031
Psrs = osr.SpatialReference()
Psrs.ImportFromEPSG(outputEPSG)


"""
