import os, shutil
import numpy as np
import xarray as xr
import urllib.request
import datetime
import time
import glob
from multiprocessing import Pool, freeze_support
#from arcpy.sa import Raster

from configs import (SPECS, skip_existing_file_check, print_debug_print_statements,
                     lightning_1min_netcdf, data_update_interval_sec,
                     data_summation_period_min)
from utils import proj
from utils.logs import logfile
import processing.netcdf as netcdf
import processing.files as file_check
import processing.downloads as downloads
import processing.calcs as calcs
#import processing.gis as gis
import processing.placefiles as placefiles

def main():
    print("--------------------------")
    print("-------Script Start-------")
    print("--------------------------\n")

    # If we're just starting the script up, make sure all directories are clean 
    file_check.initial_clean(**SPECS)

    # loop_script determines if the script should run one time, or continue to run
    # indefinitely.
    #  At the end of the main section, the script checks the control file to see if
    #  "LoopScript" is still set to True.
    loop_script = True
    while loop_script:
        #determine script start time ("now" time)
        script_run_time_utc = datetime.datetime.utcnow()    

        #retrieve list of available lightning density files from thredds catalog
        print("Retrieving netcdf file list from thredds catalog")

        netcdf_file_list = downloads.query_glm_files(script_run_time_utc, **SPECS)

        # check to see what files exist locally and what files do not exist locally.
        # Download files that do not exist locally (downloaded and converted to IMG).
        # start by assuming that the "most recent" GLM file is the earliest file in the
        # file list
        most_recent_file_date = (script_run_time_utc - SPECS["lookback_period"]
                                 - SPECS["summation_period"])
        files_to_download = []
        #netcdf_file_list = sorted(list(set(netcdf_file_list)))   

        # If no files are available, this entire block will get skipped (blank list)
        for netcdf_file in netcdf_file_list:
            netcdf_file_time = netcdf.determine_netcdf_datetime(netcdf_file)
            if netcdf_file_time > most_recent_file_date:
                most_recent_file_date = netcdf_file_time

            if not file_check.instantaneous_lightning_exists(netcdf_file_time, **SPECS) \
               and not skip_existing_file_check:
                if print_debug_print_statements:
                    log.info(f"{netcdf_file_time} Does not exist.")
                    log.info(f"  Downloading {netcdf_file}")

                # Append list of files we need to download into a new list here, then
                # perform the downloading outside the loop in a Pool
                files_to_download.append(netcdf_file)

        # Initiate a multiprocessing pool to download files that don't exist locally and
        # write to compressed binary npz files
        pool = Pool(8)
        num_files = len(files_to_download)
        pool.starmap(downloads.get_lightning_netcdf_mproc, zip(files_to_download,
                    [SPECS["thredds_download_base_url"]]*num_files,
                    [lightning_1min_netcdf]*num_files,
                    [SPECS["temp_folder"]]*num_files))
        pool.close()
        
        if len(netcdf_file_list) > 0:
            # Store most recent file time after exiting our download loop. 
            most_recent_file_date = netcdf_file_time
            
            # summation logic follows
            print(f"Creating {data_summation_period_min}-min sum of data...")
            start = script_run_time_utc - SPECS["lookback_period"]
            delta = SPECS["time_interval"]

            # Specify the last time as the most recent available 1-min GLM file on the
            # system. Otherwise, function will try to sum data that may not exist locally.
            time_list = downloads.create_time_list(start, most_recent_file_date, delta)

            # filter lat/lon based upon min/max lat/lon bounding box
            lon, lat = proj.extract_lat_lon(lightning_1min_netcdf)
            
            # Loop through the 1-minute files, compute summation period sums, and
            # output csv, shapefile, and raster file
            for time_entry in time_list:
                if not file_check.summation_lightning_exists(time_entry, **SPECS) \
                and not skip_existing_file_check:
                    sums = calcs.create_summation(time_entry, **SPECS)
                                
            #GR2Analyst Placefile.... images
            print("GR2Analyst Placefile (Images)....creating images and writing placefile...")
            is_first_image = True
            is_final_image = False

            # Loop through the summation .npz files and create .pngs.  Output placefile. 
            # Need to sort after glob to make sure we keep track of last image file which will have 
            # a different expiration time in the placefile.
            files = sorted(glob.glob(SPECS["temp_folder"] + "lightning_density_summation*.npz"))
            for image_count, sum_file in enumerate(files):
                fname = SPECS["temp_folder"] + "lightning_density_summation_%Y_%m_%d_%H%M.npz"
                data = np.load(sum_file)['a']
                
                file_date = datetime.datetime.strptime(sum_file, fname)
                out_png = SPECS["output_folder"] + "lightning_density_" + \
                        file_date.strftime("%Y_%m_%d_%H%M") + ".png"

                if (not file_check.image_placefile_exists_for_time(file_date, **SPECS)) \
                    and (not SPECS["skip_existing_file_check"]):
                    if print_debug_print_statements:
                        print("-->Does not exist for time " +
                            file_date.strftime("%Y-%m-%d %H%M UTC") + "....creating...")
                    image_info = placefiles.plot_lightning(lon, lat, data, out_png, **SPECS)
                #else:
                #    if print_debug_print_statements:
                #        print("  Data already exists, skipping.")

                if image_count+1 == len(files):
                    is_final_image = True

                placefiles.write_lightning_img(out_png, file_date, most_recent_file_date,
                                            image_info, is_first_image, is_final_image,
                                            **SPECS)
                is_first_image = False
            
            print("Copying placefiles from temp folder to output folder...")
            if os.path.exists(SPECS["temp_lightning_density_image_placefile"]):
                shutil.copy(SPECS["temp_lightning_density_image_placefile"],
                            SPECS["lightning_density_image_placefile"])

            # Purge stale data
            print("Purging stale data...")
            file_check.cleanup_files_if_outdated(script_run_time_utc, **SPECS)
        
        else:
            print("***No GLM datafiles were found online for the current period.***")
            log.warning("No GLM datafiles were found online for the current lookback period.")
            
        loop_script = True
        print(f"Pausing script for {data_update_interval_sec} seconds.\n")
        log.info("=====================================================================")
        time.sleep(data_update_interval_sec)

if __name__ == "__main__":
    log = logfile(f"{os.getlogin()}")
    freeze_support()                                         # needed for multiprocessing
    main()
