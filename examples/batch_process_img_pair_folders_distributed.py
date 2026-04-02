# ---- This is <batch_process_img_pair_folders_distributed.py> ----

"""
- Loop over a txt file with pre-processed IMG_PAIR_DIR entries (contains georeg*tif files)
- Create an individual job script for each image pair and start a separate job for:
    - DoB
    - local_std
    - normprod_smovar

User inputs:
""" 

import pathlib
from loguru import logger
import sys
import shutil

import subprocess


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
site = "Thwaites"

# Build path site-specific data dir
SITE_DIR =  DATA_DIR / f"{site}"

# Build full path to intensity geotiff dir
GEOTIFF_DIR = SITE_DIR / "GA_geotiffs"

# Provide path to input file with IMG_PAIR_DIR list
img_pair_list_path = SITE_DIR / "valid_img_pair_list.txt"

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# DEFINE PROCESSING PARAMETERS

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
logger.info(f"img_pair_list_path: {img_pair_list_path}")

# These should be located in your work folder
LIST_FILE_PATH = SITE_DIR / "Thwaites__valid_img_pair_list.txt"
TEMPLATE_FILE  = pathlib.Path("./pbs_template.txt").resolve()
RUN_SCRIPT     = pathlib.Path("./run_single_pair_as_separate_job.py").resolve()
LOG_DIR        = pathlib.Path("./batch_processing/logs").resolve()

if not LIST_FILE_PATH.is_file():
    logger.error(f"Could not find LIST_FILE_PATH: {LIST_FILE_PATH}")

if not TEMPLATE_FILE.is_file():
    logger.error(f"Could not find TEMPLATE_FILE: {TEMPLATE_FILE}")

if not RUN_SCRIPT.is_file():
    logger.error(f"Could not find RUN_SCRIPT: {RUN_SCRIPT}")


# Make sure that LOG_DIR exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Read the image directories from the list file
with open(LIST_FILE_PATH, 'r') as f:
    image_dirs = [line.strip() for line in f if line.strip()]

if not any(image_dirs):
    logger.error("Could not read any image_dirs from LIST_FILE_PATH")

# Get number of image pairs to process
n_pairs = len(image_dirs)
logger.info(f"Read {n_pairs} IMG_PAIR_DIRs from LIST_FILE_PATH")

# image_dirs must contain the full paths 
image_dirs = [ SITE_DIR/image_dir for image_dir in image_dirs ]

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Read the PBS template
with open(TEMPLATE_FILE, 'r') as f:
    pbs_template = f.read()

# Create emtpty job list
pbs_job_list = []

# Generate the PBS scripts
for IMG_PAIR_DIR in image_dirs:

    if not IMG_PAIR_DIR.is_dir():
        logger.error(f"Could not find IMG_PAIR_DIR: {IMG_PAIR_DIR}")

    img_pair_name = IMG_PAIR_DIR.name

    # Set parameters for processing in dictionary
    params = {
        "jobname": f"PBS_JOB_{img_pair_name}",
        "log_dir": LOG_DIR,
        "run_script_path": RUN_SCRIPT,
        "img_pair_dir": IMG_PAIR_DIR,
        "windows": window_list,
        "save_intermediate_products": save_intermediate_products,
        "loglevel": loglevel
    }


    # Fill PBS template and write to file
    pbs_template_filled = pbs_template.format(**params)

    pbs_script_path = f"submit_{img_pair_name}.pbs"
    
    with open(pbs_script_path, 'w') as f:
        f.write(pbs_template_filled)
    
    logger.info(f"Generated PBS script for {img_pair_name}: {pbs_script_path}")

    pbs_job_list.append(pbs_script_path)


for pbs_job in pbs_job_list:

    subprocess.run(["qsub", pbs_job])




