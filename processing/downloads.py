from processing.netcdf import determine_netcdf_datetime, write_to_numpy
import urllib
import os 
import pandas as pd 

def find_files(catalog_url, regex):
    """
    Query the THREDDS server catalogue listing and return the available files following
    a specific regular expression.

    Parameters:
    -----------
    catalog_url : string
        Full url path to THREDDS catalog

    regex: string

    """
    import re
    try:
        import urllib2 as urlreq
    except ImportError:
        import urllib.request as urlreq

    file_list = []
    req = urlreq.Request(catalog_url)
    result = urlreq.urlopen(req)
    txt = result.read().decode('utf-8')
    file_list = re.findall(regex, txt)
    file_list.sort()
    return file_list

def create_time_list(start_time, end_time, interval):
    """
    Create a list of dates/times that fall within a start and end time based on a
    specified time interval. Returns a list of datetime objects.

    """
    times = pd.date_range(start_time, end_time, freq=interval).strftime("%Y-%m-%d %H:%M")
    return times.tolist()

def query_glm_files(script_run_time_utc, **kwargs):
    """
    Create list of dates/times that fall within the lookback period, plus the
    summation period

    """
    start = (script_run_time_utc - kwargs.get("lookback_period")
             - kwargs.get("summation_period"))
    end = script_run_time_utc
    delta = kwargs.get("time_interval")
    time_list = create_time_list(start, end, delta)

    #retrieve all thredds catalog entries for GLM lightning density data
    regex = "OR_GLM-L2-GLMC-M3_G16_s[\d]{14}_e[\d]{14}_c[\d]{14}.nc"
    netcdf_file_list = find_files(kwargs.get("thredds_catalog_url"), regex)

    #loop through list of available netcdf files from thredds catalog, check to see if
    #their times match desired time list. If in the desired time list, add filename to
    #final list. 
    filtered_file_list = []
    for netcdf_file in netcdf_file_list:
        netcdf_file_time = determine_netcdf_datetime(netcdf_file)
        for temp_time in time_list:
            if netcdf_file_time.strftime("%Y-%m-%d %H:%M") == temp_time:
                filtered_file_list.append(netcdf_file)
    
    # Remove duplicate entries
    filtered_file_list = sorted(set(filtered_file_list))
    
    #write filtered list of netcdf files to a file. This section is mostly for debugging
    #and could be removed later for efficiency
    filename = kwargs.get("input_folder") + "netcdf_file_list.txt"
    with open(filename, "w") as f:
        for netcdf_file in filtered_file_list: f.write(netcdf_file + "\n")

    # For missing datafile testing...just removing a file from the download queue
    #filtered_file_list.pop(-10)
    #filtered_file_list.pop(-11)
    #filtered_file_list.pop(-9)
    #filtered_file_list.pop(-20)
    #filtered_file_list = []

    return filtered_file_list

def get_lightning_netcdf_mproc(netcdf_filename, base_url, temp_local_netcdf_filename,
                               npz_directory):
    """
    Download a specific GLM netcdf file from the THREDDS server. Save it to a temporary
    file on the local disk.

    """
    temp_local_netcdf_filename = f"{temp_local_netcdf_filename}.{os.getpid()}"
    urllib.request.urlretrieve(base_url + netcdf_filename,
                               temp_local_netcdf_filename)

    write_to_numpy(temp_local_netcdf_filename, npz_directory)
