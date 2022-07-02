import datetime
import xarray as xr
import numpy as np

def determine_netcdf_datetime(netcdf_file):
    start_date_string = netcdf_file[23:34]
    end_date_string = netcdf_file[39:50]
    #start_date = datetime.datetime.strptime(start_date_string, "%Y%j%H%M")
    end_date = datetime.datetime.strptime(end_date_string, "%Y%j%H%M")
    return end_date

def write_to_numpy(netcdf_file, outdir):
    ds = xr.open_dataset(netcdf_file)
    file_time = datetime.datetime.strptime(ds.time_coverage_end, "%Y-%m-%dT%H:%M:%SZ")
    savename = f"{outdir}lightning_density_1min_{file_time.strftime('%Y_%m_%d_%H%M')}"
    np.savez_compressed(savename, a=ds.flash_extent_density.values)
    return
