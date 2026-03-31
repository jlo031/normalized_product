# ---- This is <normprod_utils.py> ----

"""
Module with helpers for normprod (normalized product) computation.
Developed as part of the AAPP/UTAS tool for Antarctic fast ice mapping.

Initial developments by A.P. Doulgeris, G. Burke, A. Fraser.

Packaged by J. Lohse.
(johannes.lohse@utas.edu.au)
"""

import pathlib
from loguru import logger

from datetime import datetime

import numpy as np
from scipy.ndimage import uniform_filter

from osgeo import gdal, osr

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def check_raster_stats(filepath):
    """Prints min, max, mean, and std of a raster file."""

    filepath = pathlib.Path(filepath)

    if not filepath.is_file():
        logger.error(f"Cannot find filepath: {filepath}.")
        return
    
    ds = gdal.Open(filepath, gdal.GA_ReadOnly)
    if ds is None:
        logger.error(f"Cannot open filepath: {filepath}.")
        return
    
    arr = ds.GetRasterBand(1).ReadAsArray()
    print(f"Stats for: {filepath.name}:")
    print(f"    Full path: {filepath}")
    print(f"    Min: {np.nanmin(arr)}")
    print(f"    Max: {np.nanmax(arr)}")
    print(f"    Mean: {np.nanmean(arr)}")
    print(f"    Std Dev: {np.nanstd(arr)}\n")
    ds = None

    return

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def fill_nans(image):
    """Fills NaNs before filtering to prevent them from growing."""

    nan_mask = np.isnan(image)

    # If no NaNs, return original
    if not np.any(nan_mask):
        return image

    logger.debug("Filling NaNs of input image.")

    # Simple approach: replace NaNs with the local mean of valid pixels
    mean_value = np.nanmean(image)
    image_filled = np.where(nan_mask, mean_value, image)

    return image_filled

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# NEEDED? SAME AS np.nanmean ?

def nan_safe_mean_filter(values):
    """Computes the mean of non-NaN values."""

    valid_values = values[~np.isnan(values)]

    return np.nan if valid_values.size == 0 else np.mean(valid_values)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# VERY SPECIFIC TO FILENAME CONVENTION, WILL BREAK AT THE SLIGHTEST CHANGE
# SHOULD IDEALLY NOT BE PART OF THE PACKAGE
# IMPLEMENTED ALTERNATIVE 'date1', 'date2' inputs in 'check_and_trim_image_pair'

def extract_date_from_filename(filename):
    """Convert date from GA S1 filename to datetime.datetime"""

    # Extract datestring from filename
    datestring = filename[12:27]

    date = extract_date_from_datestring(datestring)

    return date

# --------------------- #

def extract_date_from_datestring(datestring):
    """Convert datestring (YYYYMMDDThhmmss) to datetime.datetime"""

    logger.debug(f"datestring: {datestring}")

    # Convert to datetime
    try:
        date = datetime.strptime(datestring, "%Y%m%dT%H%M%S")
    except ValueError:
        logger.error(f"Extracted datestring does not match the expected format.")
        date = None

    return date

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def get_valid_data_extent(ds):
    """Compute the bounding box of the valid (non-NaN) data in a GDAL dataset."""

    band = ds.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    
    arr = band.ReadAsArray()
    
    # Create a valid mask: Exclude nodata and NaN values
    if nodata is not None:
        mask = (arr != nodata) & ~np.isnan(arr)
    else:
        mask = ~np.isnan(arr)  # Assuming float data with NaNs

    if not np.any(mask):  # No valid data
        return None

    # Get min/max row/col indices where data is valid
    row_indices = np.where(np.any(mask, axis=1))[0]
    col_indices = np.where(np.any(mask, axis=0))[0]

    if row_indices.size == 0 or col_indices.size == 0:
        return None  # No valid pixels found

    min_row, max_row = row_indices[0], row_indices[-1]
    min_col, max_col = col_indices[0], col_indices[-1]

    # Convert pixel coordinates to geographic coordinates
    geotransform = ds.GetGeoTransform()
    xRes, yRes = abs(geotransform[1]), abs(geotransform[5])  # Pixel size
    min_x = geotransform[0] + geotransform[1] * min_col
    max_x = geotransform[0] + geotransform[1] * (max_col + 1)
    max_y = geotransform[3] + geotransform[5] * min_row
    min_y = geotransform[3] + geotransform[5] * (max_row + 1)

    return (min_x, min_y, max_x, max_y, xRes, yRes)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def check_and_trim_image_pair(
    img_pair,
    output_dir,
    min_temp_baseline = 11.9,
    max_temp_baseline = 12.1,
    output_epsg = 3031,
    date1 = None,
    date2 = None,
    overwrite = False
):
    """
    Check input image pair for spatial overlap and temporal baseline requirements.
    Trim to common valid overlap region and write resulting geotiff images to output dir.

    Parameters
    ----------
    img_pair : Image pair list with full paths to input images
    output_dir : path to directory where trimmed outputs are stored
    min_temp_baseline : minimum temporal baseline in days (default=11.9)
    min_temp_baseline : maximum temporal baseline in days (default=12.1)
    output_epsg : EPSG code for output image projection (default=3031)
    date1 : manual datestring for first image of pair (default=None)
    date2 : manual datestring for second image of pair (default=None)
    overwrite : overwrite previous existing results (default=False)

    Returns
    -------
    """

    logger.info("Starting to check and trim input image pair...")

    # Check input image pair
    if not isinstance(img_pair, list):
        logger.error(f"Expected input img_pair of type 'list' but received {type(image_pair).__name__}.")
        return False

    if not len(img_pair)==2:
        logger.error(f"Input img_pair list must have exactly 2 entries.")
        return False

    # Set inddividual paths to both input images
    img_path_1 = pathlib.Path(img_pair[0])
    img_path_2 = pathlib.Path(img_pair[1])

    logger.debug(f"img_path_1: {img_path_1}")
    logger.debug(f"img_path_2: {img_path_2}")

    # Check that both image files exist
    if not img_path_1.is_file():
        logger.error(f"Could not find first input image: {img_path_1}")
        return False

    if not img_path_2.is_file():
        logger.error(f"Could not find second input image: {img_path_2}")
        return False

# --------------------- #

    # Set/extract dates
    # 'extract_date' implemented in this module is VERY specific to GA naming convention
    # If this fails, 'date1' and 'date2' can be defined as external input parameters

    if date1==None:
        date1 = extract_date_from_filename(img_path_1.name)
    else:
        date1 = extract_date_from_datestring(date1)

    if date2==None:
        date2 = extract_date_from_filename(img_path_2.name)
    else:
        date2 = extract_date_from_datestring(date2)

    logger.debug(f"date1: {date1}")
    logger.debug(f"date2: {date2}")

    if date1==None or date2==None:
        logger.error("Could not succesfully convert dates to datetime objects.")
        logger.error("Check filename convenction or provide datestring as 'YYYYMMDDThhmmss'.")
        return False	

    # Calculate temporal baseline in days
    temp_baseline = date2 - date1
    temp_baseline_days = np.abs(temp_baseline.total_seconds()) / 86400

    logger.debug(f"temp_baseline_days: {temp_baseline_days}")

    if not (min_temp_baseline <= temp_baseline_days <= max_temp_baseline):
        logger.info(f"skipping this pair because temporal baseline is outside of defined range.")
        return False

# --------------------- #

    # Ensure that output_dir exists
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build full output paths
    georeg1_path = output_dir / f"georeg_1_{date1.strftime('%Y%m%d')}_EPSG{output_epsg}.tif"
    georeg2_path = output_dir / f"georeg_2_{date2.strftime('%Y%m%d')}_EPSG{output_epsg}.tif"

    logger.debug(f"georeg1_path: {georeg1_path}")
    logger.debug(f"georeg2_path: {georeg2_path}")

    if georeg1_path.is_file() and georeg2_path.is_file() and not overwrite:
        logger.info(f"Trimmed output files already exist. Set 'overwrite' option to reprocess.")
        return True

    elif georeg1_path.is_file() or georeg2_path.is_file() and overwrite:
        logger.info(f"Removing existing output files before reprocessing")
        georeg1_path.unlink(missing_ok=True)
        georeg1_path.unlink(missing_ok=True)

# --------------------- #

    logger.info("Passed initial checks, reading data and checking valid extent...")

    # Open data sets
    DS1 = gdal.Open(img_path_1, gdal.GA_ReadOnly)
    DS2 = gdal.Open(img_path_2, gdal.GA_ReadOnly)

    # Get image extent
    extent1 = get_valid_data_extent(DS1)
    extent2 = get_valid_data_extent(DS2)

    logger.debug(f"extent1: {extent1}")
    logger.debug(f"extent2: {extent2}")

    # Compute the intersection of the extents
    if extent1 and extent2:
        min_x = max(extent1[0], extent2[0])  # Max of min_x
        min_y = max(extent1[1], extent2[1])  # Max of min_y
        max_x = min(extent1[2], extent2[2])  # Min of max_x
        max_y = min(extent1[3], extent2[3])  # Min of max_y
        xRes = min(extent1[4], extent2[4])  # Use the finer resolution
        yRes = min(extent1[5], extent2[5])  

        # Check if valid intersection exists
        if min_x >= max_x or min_y >= max_y:
            logger.info(f"Skipping this pair because of no overlapping valid region.")
            return False

    else:
        logger.info(f"Skipping this pair because one image does not contain valid data.")
        return False

# --------------------- #

    logger.info("Warping both images to common projection and overlapping footprint...")

    # Specify output spatial reference system    
    Psrs = osr.SpatialReference()
    Psrs.ImportFromEPSG(output_epsg)
    logger.debug(f"Initialized spatial reference system: EPSG {Psrs.GetAuthorityCode(None)}, {Psrs.GetName()}")

    # Gdalwarp the input bands to the new projection and extent
    gdal.Warp(
        georeg1_path,
        DS1,
        format = "GTiff",
        dstSRS = Psrs,
        outputBounds = (min_x, min_y, max_x, max_y), 
        xRes = xRes,
        yRes = yRes,
        dstNodata = np.nan,
        outputType=gdal.GDT_Float32,
        creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES"]
    )

    # Gdalwarp the input bands to the new projection and extent
    gdal.Warp(
        georeg2_path,
        DS2,
        format = "GTiff",
        dstSRS = Psrs,
        outputBounds = (min_x, min_y, max_x, max_y), 
        xRes = xRes,
        yRes = yRes,
        dstNodata = np.nan,
        outputType=gdal.GDT_Float32,
        creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES"]
    )

    # Clean up
    DS1, DS2 = None, None

# --------------------- #

    logger.info("Trimming reprojected images and to common valid points...")

    # Read in warped images
    DS1 = gdal.Open(georeg1_path, gdal.GA_Update)
    DS2 = gdal.Open(georeg2_path, gdal.GA_Update)
    Dat1, Dat2 = DS1.ReadAsArray(), DS2.ReadAsArray()

    # Get number of bands and expand dims if just one band
    NBnds1, NBnds2 = DS1.RasterCount, DS2.RasterCount
    if NBnds1 == 1:
        Dat1 = np.expand_dims(Dat1, 0)
    if NBnds2 == 1:
        Dat2 = np.expand_dims(Dat2, 0)

    # Find all indices that are valid in both images
    Intersection = ~np.isnan(Dat1[0]) & ~np.isnan(Dat2[0])

    # Check all bands in both images
    # Not tested - GA images only contain one single band per file
    if NBnds1 > 1:
        Intersection &= ~np.isnan(Dat1[1]) & ~np.isnan(Dat2[1])

    # Set all non-valid data points in all bands to np.nan
    for di in range(NBnds1):
        Dat1[di][~Intersection] = np.nan
        Bnd1 = DS1.GetRasterBand(di+1)
        Bnd1.WriteArray(np.float32(Dat1[di]))
        Bnd1.SetNoDataValue(np.nan)
        Bnd1.FlushCache()

    # Set all non-valid data points in all bands to np.nan
    for di in range(NBnds2):
        Dat2[di][~Intersection] = np.nan
        Bnd2 = DS2.GetRasterBand(di+1)
        Bnd2.WriteArray(np.float32(Dat2[di]))
        Bnd2.SetNoDataValue(np.nan)
        Bnd2.FlushCache()

    # Clean up
    DS1.FlushCache()
    DS1 = None
    DS2.FlushCache()
    DS2 = None

    return True

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <normprod_utils.py> ----
