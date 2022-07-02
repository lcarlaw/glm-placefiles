from processing.downloads import create_time_list
import datetime
import numpy as np
import os
import xarray as xr 

from utils.logs import logfile
import processing.files as file_check
log = logfile(f"{os.getlogin()}")

def create_summation(file_datetime, **kwargs):
    """
    Sum the 1-minute GLM datafiles over the defined summation period (usually 5 minutes)
    and output associated 2-d arrays of data in compressed numpy files. Output image
    file along with appropriate coordinates for reading in GR

    """
    summation_period = kwargs.get("summation_period")
    data_time_interval = kwargs.get("time_interval")
    temp_folder = kwargs.get("temp_folder")
    file_datetime = datetime.datetime.strptime(file_datetime, "%Y-%m-%d %H:%M")
    temp_time_list = create_time_list(file_datetime-summation_period, file_datetime,
                                      data_time_interval)[1:]
    
    summation_file_list = []
    for time_entry in temp_time_list:
        time_entry = datetime.datetime.strptime(time_entry, "%Y-%m-%d %H:%M")
        filename = f"lightning_density_1min_{time_entry.strftime('%Y_%m_%d_%H%M')}.npz"

        # Need to check if data is missing here. If netcdf files weren't downloaded or 
        # available, the corresponding .npz file will be missing from the file system.
        file_exists = file_check.instantaneous_lightning_exists(time_entry, **kwargs)
        if file_exists: 
            summation_file_list.append(temp_folder + filename)

    # Summation. Currently, if any files are missing from the rolling 5-minute window, 
    # entire GLM image is set to 0
    sums = 0.
    if len(summation_file_list) >= 4:
        for f in summation_file_list:
            data = np.nan_to_num(np.load(f)['a'])
            sums = sums + data
        if len(summation_file_list) == 4:
            print(f"-->***Missing 1 minute of data during {temp_time_list[-1]} summation period.")
            log.warning(f"-->***Missing 1 minute of data during {temp_time_list[-1]} summation period.")
    else:
        print(f"-->***Missing >1 minute of data during {temp_time_list[-1]} summation period.")
        log.warning(f"-->Missing >1 minute of data during {temp_time_list[-1]} summation period.")
        ds = xr.open_dataset(kwargs.get("lightning_1min_netcdf"))
        sums = np.zeros_like(ds.flash_extent_density, dtype=float)

    sums[sums == 0] = np.nan
    outdir = kwargs.get("temp_folder")
    file_time = file_datetime
    savename = f"{outdir}/lightning_density_summation_{file_time.strftime('%Y_%m_%d_%H%M')}"
    np.savez_compressed(savename, a=sums)

    return sums
