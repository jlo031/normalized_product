# ---- This is <normprod.py> ----

"""
Module for normprod (normalized product) computation.
Developed as part of the AAPP/UTAS tool for Antarctic fast ice mapping.

Initial developments by A.P. Doulgeris, G. Burke, A. Fraser.

Packaged by J. Lohse.
(johannes.lohse@utas.edu.au)
"""

import pathlib
from loguru import logger

import numpy as np
from scipy.ndimage import uniform_filter, generic_filter

from osgeo import gdal

from mormalized_product import normprod_utils

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def compute_DoB(image_path, output_path, window):
    """Computes the difference from 2D boxcar smoothing (boxcar DoG-like) while preventing NaN spread."""

    logger.info(f"Starting DoB computation for w={window}...")

    image_path  = pathlib.Path(image_path)
    output_path = pathlib.Path(output_path)

    logger.debug(f"image_path:  {image_path}")
    logger.debug(f"output_path: {output_path}")
    logger.debug(f"window:      {window}")

    if output_path.is_file():
        logger.info(f"Skipping, {output_path} already exists.")
        return True

    if not image_path.is_file():
        logger.error(f"Could not find image_path: {image_path}.")
        return False

    ds = gdal.Open(image_path, gdal.GA_ReadOnly)
    if ds is None:
        logger.error(f"Cannot open image_path: {image_path}")
        return False

    # Get input band (can be HH or HV, input image, but should just have one single band
    band = ds.GetRasterBand(1).ReadAsArray()

    # Fill NaNs before filtering
    band_filled = normprod_utils.fill_nans(band)

    # Apply 2D boxcar filter
    smoothed = uniform_filter(band_filled, size=window, mode="nearest")

    # Difference from smoothed version
    DoB = band - smoothed

# --------------------- #

    # Save result
    driver = gdal.GetDriverByName("GTIFF")
    out_ds = driver.Create(output_path, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(DoB)
    out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
    out_ds.FlushCache()

    # Clean up
    out_ds = None
    ds = None

    logger.info(f"Saved DoB image: {output_path}")

    return output_path

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def compute_local_std(image_path, output_path, window):
    """Computes the local standard deviation in a boxcar window of given width."""

    logger.info(f"Starting local std computation for w={window}...")

    image_path  = pathlib.Path(image_path)
    output_path = pathlib.Path(output_path)

    if output_path.is_file():
        logger.info(f"Skipping, {output_path} already exists.")
        return output_path

    if not image_path.is_file():
        logger.error(f"Could not find image_path: {image_path}.")
        return

    ds = gdal.Open(image_path, gdal.GA_ReadOnly)
    if ds is None:
        logger.error(f"Cannot open image_path: {image_path}")
        return

    # Get input band (can be HH or HV, input image, but should just have one single band
    band = ds.GetRasterBand(1).ReadAsArray()

    # Fill NaNs before filtering
    band_filled = normprod_utils.fill_nans(band)

    # Compute mean and mean of squares in local window
    local_mean = uniform_filter(band_filled, size=window, mode="nearest")
    local_mean_sq = uniform_filter(band_filled**2, size=width, mode="nearest")

    # Standard deviation: sqrt(E[x^2] - (E[x])^2)
    local_std = np.sqrt(local_mean_sq - local_mean**2)

# --------------------- #

    # Save result
    driver = gdal.GetDriverByName("GTIFF")
    out_ds = driver.Create(output_path, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(local_std)
    out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
    out_ds.FlushCache()

    # Clean up
    out_ds = None
    ds = None

    logger.info(f"Saved local std image: {output_path}")

    return output_path

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def compute_normprod(
    dob1,
    dob2,
    std1,
    std2,
    normprod_smovar_output_path,
    window,
    save_intermediate_products=False
):
    """Computes Normalized Product (NormProd) using precomputed smoothed images, with NaN-safe summation.

    Parameters
    ----------
    dob1 : path to input DoB image 1
    dob2 : path to input DoB image 2
    std1 : path to input local std image 1
    std2 : path to input local std image 2
    normprod_smovar_output_path : path to output file, normprod divided by smoothed variance
    window : window size for normalized product (e.g. 11, 21, 33)
    """

    logger.info(f"Starting normprod_smovar computation for w={window}...")

    dob1 = pathlib.Path(dob1)
    dob2 = pathlib.Path(dob2)
    std1 = pathlib.Path(std1)
    std2 = pathlib.Path(std2)
    normprod_smovar_output_path = pathlib.Path(normprod_smovar_output_path)

    if normprod_smovar_output_path.is_file():
        logger.info(f"Skipping, {normprod_smovar_output_path} already exists.")
        return True

    if not dob1.is_file():
        logger.error(f"Could not find dob1: {dob1}.")
        return False

    if not dob2.is_file():
        logger.error(f"Could not find dob2: {dob2}.")
        return False

    if not std1.is_file():
        logger.error(f"Could not find std1: {std1}.")
        return False

    if not std2.is_file():
        logger.error(f"Could not find std2: {std2}.")
        return False

# --------------------- #

    # Read all input data

    ds_dob1 = gdal.Open(dob1, gdal.GA_ReadOnly)
    ds_dob2 = gdal.Open(dob2, gdal.GA_ReadOnly)
    ds_std1 = gdal.Open(std1, gdal.GA_ReadOnly)
    ds_std2 = gdal.Open(std2, gdal.GA_ReadOnly)

    if not all([ds_dob1, ds_dob2, ds_std1, ds_std2]):
        logger.error(f"Could not open all required input files.")
        return False

    logger.debug("Reading input data.")
    dob1 = ds_dob1.GetRasterBand(1).ReadAsArray()
    dob2 = ds_dob2.GetRasterBand(1).ReadAsArray()
    std1 = ds_std1.GetRasterBand(1).ReadAsArray()
    std2 = ds_std2.GetRasterBand(1).ReadAsArray()    

# --------------------- #

    # Compute mean of std images
    logger.debug("Computing stdmean.")
    stdmean = np.mean(np.stack([std1, std2], axis=0), axis=0)

    if save_intermediate_products:
        logger.debug("Saving stemean...")
        intermediate_output_path = normprod_smovar_output_path.parent / "stdmean.tif"
        driver = gdal.GetDriverByName("GTIFF")
        out_ds = driver.Create(intermediate_output_path, ds_dob1.RasterXSize, ds_dob1.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
        out_ds.SetGeoTransform(ds_dob1.GetGeoTransform())
        out_ds.SetProjection(ds_dob1.GetProjection())
        out_ds.GetRasterBand(1).WriteArray(stdmean)
        out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
        out_ds.FlushCache()
        out_ds = None
        logger.debug(f"Saved stdmean image: {intermediate_output_path}")

# --------------------- #

    # Square stdmean to get varianve
    logger.debug("Computing variance.")
    variance = stdmean*stdmean

    # Fill NaNs (again, just in case)
    logger.debug("Filling nans.")
    variance_filled = normprod_utils.fill_nans(variance)

    # Clean up
    stdmean = variance = None

    if save_intermediate_products:
        logger.debug("Saving intermediate output: variance.")
        intermediate_output_path = normprod_smovar_output_path.parent / "variance.tif"
        driver = gdal.GetDriverByName("GTIFF")
        out_ds = driver.Create(intermediate_output_path, ds_dob1.RasterXSize, ds_dob1.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
        out_ds.SetGeoTransform(ds_dob1.GetGeoTransform())
        out_ds.SetProjection(ds_dob1.GetProjection())
        out_ds.GetRasterBand(1).WriteArray(variance_filled)
        out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
        out_ds.FlushCache()
        out_ds = None
        logger.debug(f"Saved variance image: {intermediate_output_path}")

# --------------------- #

    # Compute smothed variance with boxcar of size window
    logger.debug("Computing smoothed variance.")
    smoothed_variance = uniform_filter(variance_filled, size=window, mode="nearest")

    if save_intermediate_products:
        logger.debug("Saving intermediate output: smoothed_variance.")
        intermediate_output_path = normprod_smovar_output_path.parent / "smoothed_variance.tif"
        driver = gdal.GetDriverByName("GTIFF")
        out_ds = driver.Create(intermediate_output_path, ds_dob1.RasterXSize, ds_dob1.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
        out_ds.SetGeoTransform(ds_dob1.GetGeoTransform())
        out_ds.SetProjection(ds_dob1.GetProjection())
        out_ds.GetRasterBand(1).WriteArray(smoothed_variance)
        out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
        out_ds.FlushCache()
        out_ds = None
        logger.debug(f"Saved smoothed_variance image: {intermediate_output_path}")

    # Clean up
    variance_filled = None

# --------------------- #

    # Compute NormProd: DoB1*DoB2
    logger.debug("Computing normprod.")
    normprod = dob1 * dob2

    if save_intermediate_products:
        logger.debug("Saving intermediate output: normprod.")
        intermediate_output_path = normprod_smovar_output_path.parent / "normprod.tif"
        driver = gdal.GetDriverByName("GTIFF")
        out_ds = driver.Create(intermediate_output_path, ds_dob1.RasterXSize, ds_dob1.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
        out_ds.SetGeoTransform(ds_dob1.GetGeoTransform())
        out_ds.SetProjection(ds_dob1.GetProjection())
        out_ds.GetRasterBand(1).WriteArray(normprod)
        out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
        out_ds.FlushCache()
        out_ds = None
        logger.debug(f"Saved normprod image: {intermediate_output_path}")

# --------------------- #

    # Apply a NaN-safe mean using generic_filter
    kernel = np.ones((window, window))  # Window for summation

    logger.debug("Starting generic_filter... about 10 mins for 11*11, 12 mins for 21*21.")

    summed_normprod = generic_filter(normprod, normprod_utils.nan_safe_mean_filter, footprint=kernel, mode='constant', cval=np.nan)

    logger.debug("Finished generic_filter")

    if save_intermediate_products:
        logger.debug("Saving intermediate output: summed_normprod.")
        intermediate_output_path = normprod_smovar_output_path.parent / "summed_normprod.tif"
        driver = gdal.GetDriverByName("GTIFF")
        out_ds = driver.Create(intermediate_output_path, ds_dob1.RasterXSize, ds_dob1.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
        out_ds.SetGeoTransform(ds_dob1.GetGeoTransform())
        out_ds.SetProjection(ds_dob1.GetProjection())
        out_ds.GetRasterBand(1).WriteArray(summed_normprod)
        out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
        out_ds.FlushCache()
        out_ds = None
        logger.debug(f"Saved summed_normprod image: {intermediate_output_path}")

    # Clean up
    variance_filled = None

# --------------------- #

    # Divide normprod by smoothed variance
    normprod_smovar = summed_normprod/smoothed_variance

    # Clean up
    summed_normprod = smoothed_variance = None

# --------------------- #

    # Write normprod_smovar to disk

    logger.debug("Saving normprod_smovar.")

    driver = gdal.GetDriverByName("GTIFF")
    out_ds = driver.Create(normprod_smovar_output_path, ds_dob1.RasterXSize, ds_dob1.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=DEFLATE", "BIGTIFF=YES"])
    out_ds.SetGeoTransform(ds_dob1.GetGeoTransform())
    out_ds.SetProjection(ds_dob1.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(normprod_smovar)
    out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
    out_ds.FlushCache()
    out_ds = None

    logger.debug("Saved normprod_smovar.")

    # Clean up
    logger.debug("Freeing memory.")
    dob1 = dob2 = std1 = std2 = ds_dob1 = ds_dob2 = ds_std1 = ds_sdt2 = None
    normprod_smovar = None

# --------------------- #

    return True

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <normprod.py> ----
