import os
from glob import glob
import re
import datetime
from utils.logs import logfile
log = logfile(f"{os.getlogin()}")

def image_placefile_exists_for_time(data_datetime, **kwargs):
    datestring = data_datetime.strftime("%Y_%m_%d_%H%M")
    filename = f"{kwargs.get('output_folder')}/lightning_density_{datestring}.png"
    if os.path.exists(filename): return True

def instantaneous_lightning_exists(data_datetime, **kwargs):
    if os.path.exists(kwargs.get("temp_folder")
        + data_datetime.strftime("lightning_density_1min_%Y_%m_%d_%H%M.npz")):
        return True

def summation_lightning_exists(data_datetime, **kwargs):
    data_datetime = datetime.datetime.strptime(data_datetime, "%Y-%m-%d %H:%M")
    filename = (kwargs.get("temp_folder")
               + f"lightning_density_summation_{data_datetime.strftime('%Y_%m_%d_%H%M')}.npz")
    if os.path.exists(filename): return True

def remove_lightning_netcdf(input_folder):
    """
    Remove the lighting netcdf files from the input directory. This includes the .xxxx 
    files acquired by the thread pool executor. 
    
    """
    raw_netcdf_files = glob(f"{input_folder}/.lightning_density_netcdf.nc.*")
    for f in raw_netcdf_files:
        log.info("Removing..." + f)
        os.remove(f)

def initial_clean(**kwargs):
    """
    Ensures all directories are cleaned on script start-up. While we shouldn't have any
    non .npz or .png files in either the temp or output folder, check just in case 
    since it's easy, and only delete those. Remove any lightning netcdf files and old 
    placefiles. 

    """
    folders = [
        kwargs.get("temp_folder"),
        kwargs.get("output_folder"),
        ]

    for folder in folders: 
        files = glob(f"{folder}/*")
        for f in files: 
            if f[-3:] in ["npz", "png"]:
                os.remove(f)

    remove_lightning_netcdf(kwargs.get("input_folder"))

    placefiles = [
        kwargs.get("lightning_density_image_placefile"),
        kwargs.get("temp_lightning_density_image_placefile")
    ]
    for placefile in placefiles:
        if os.path.exists(placefile): os.remove(placefile)

def cleanup_files_if_outdated(script_run_time_utc, **kwargs):
    """
    Search through the various directories for stale files and remove them from the disk.

    """

    # Subtract a minute here so that we don't delete the oldest file, only to re-download
    # it again at the top of the next loop.
    start_time = (script_run_time_utc - kwargs.get("lookback_period")
                  - kwargs.get("summation_period")) - datetime.timedelta(minutes=1)

    folders = [
        kwargs.get("temp_folder")
        ]

    regex = "[\d]{4}_[\d]{2}_[\d]{2}_[\d]{4}"
    for folder in folders:
        files = sorted(glob(f"{folder}/*"))
        for f in files:
            datestring = re.findall(regex, f)
            if len(datestring) == 1:
                file_date = datetime.datetime.strptime(datestring[0], '%Y_%m_%d_%H%M')
                if file_date < start_time:
                    log.info("Removing..." + f)
                    os.remove(f)
            else:
                # We did not find any files satisfying our regex search
                pass

    # Remove the netcdf files with appended pids from the multiproc download step.
    remove_lightning_netcdf(kwargs.get("input_folder"))
