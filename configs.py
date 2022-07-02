import datetime
import os

##########################################################################################
# Variables
#
# directories
current_folder = os.getcwd()
input_folder = current_folder + "\\input\\"
temp_folder = current_folder + "\\temp\\"
arcpro_folder = current_folder + "\\arcpro\\"
output_folder = current_folder + "\\output\\"
control_file = input_folder + "control_file.txt"

input_folder = current_folder + "/input/"
temp_folder = current_folder + "/temp/"
output_folder = current_folder + "/output/"

#
# temp files
lightning_1min_netcdf = input_folder + ".lightning_density_netcdf.nc"
temp_lightning_density_1min_csv_file = temp_folder + "temp_lightning_csv.csv"
temp_lightning_density_1min_shp_file = temp_folder + "temp_lightning_shp.shp"
temp_lightning_density_1min_raster_file = temp_folder + "temp_lightning_raster.img"            #from IDW interpolation of raw shapefile
temp_lightning_density_sum_raster_file = temp_folder + "temp_lightning_raster_summation.img"   #running summation of lightning density raster
temp_lightning_density_contour_file = temp_folder + "temp_lightning_contour.shp"
temp_lightning_density_image_placefile = temp_folder + "temp_lightning_placefile_image.txt"
temp_lightning_density_icons_placefile = temp_folder + "temp_lightning_placefile_icons.txt"
temp_lightning_density_points_placefile = temp_folder + "temp_lightning_placefile_points.txt"
temp_lightning_density_contours_placefile = temp_folder + "temp_lightning_placefile_contours.txt"


temp_summation_csv = temp_folder + "temp_lightning_csv.csv"
temp_summation_shp = temp_folder + "temp_lightning_shp.shp"
temp_summation_raster = temp_folder + "temp_lightning_raster.img" 

#
# data extents
min_lat =  35   ##39.5
max_lat =  45   ##43.5
min_lon = -92   ##-91.0
max_lon = -82   ##-86.0

#
# URLs
thredds_catalog_url = "https://thredds.ucar.edu/thredds/catalog/satellite/goes/east/products/GLMISatSS/Level2/FullDisk/current/catalog.html"
thredds_download_base_url = "https://thredds.ucar.edu/thredds/fileServer/satellite/goes/east/products/GLMISatSS/Level2/FullDisk/current/"

#
# ArcPro
#arcpro_extent = arcpy.Extent(min_lon, min_lat, max_lon, max_lat)
#arcpro_template_file = arcpro_folder + "GR_Lightning_Template.aprx"
#image_size = 1600                                                  #controls the size of the image exported by ArcPro, which controls resolution in GR2Analyst

#
#GR
lightning_density_image_placefile = output_folder + "Lightning_Placefile_image.txt"
lightning_density_icons_placefile = output_folder + "Lightning_Placefile_icons.txt"
lightning_density_points_placefile = output_folder + "Lightning_Placefile_points.txt"
lightning_density_contours_placefile = output_folder + "Lightning_Placefile_contours.txt"
lightning_density_value_breaks_for_placefile_icons = [0.001,0.50,2.5,5.0,25.0,100.0,250.00,10000.00]
placefile_icon_file = output_folder + "GR_placefile_icons.png"

#
# other
data_time_interval_min = 1
data_lookback_period_min = 60         #how far back in time from now should the script look for lightning data?
data_summation_period_min = 5         #over what period should lightning data be added together for running totals?
data_expiration_min = 10              #after how many minutes should lightning data be considered "old" and no longer display with newer radar data?
data_update_interval_sec = 20         #time to wait, in seconds, between runs of the script to update of GLM data
raw_data_resolution_deg = 0.03        #resolution, in decimal degrees of lat/lon, that is the largest of either the lat or lon grid spacing in the raw netcdf data
interpolation_resolution_deg = 0.05   #resolution, in decimal degrees of lat/lon, of IDW interpolation raster or resampling raster
skip_existing_file_check = False      #only set to true if the domain has changed. If True, all files are downloaded and local files overidden.
print_debug_print_statements = True  #if true, extra statements are printed during code execution which may help with debug; if false, only limited statements are printed

##########################################################################################

colors = ['#0000b8', '#0000b9', '#0100b9', '#0101ba', '#0201ba', '#0201bb', '#0301bb', 
           '#0301bb', '#0401bd', '#0402be', '#0502be', '#0502be', '#0602be', '#0602c0', 
           '#0602c1', '#0603c1', '#0803c1', '#0803c3', '#0903c3', '#0903c4', '#0a03c4', 
           '#0a04c5', '#0b04c6', '#0b04c6', '#0c04c7', '#0c04c8', '#0d04c8', '#0d05c9', 
           '#0d05c9', '#0d05ca', '#0f05cb', '#0f05cb', '#1005cc', '#1006cd', '#1106cd', 
           '#1106ce', '#1206ce', '#1206ce', '#1306d0', '#1306d0', '#1406d1', '#1406d1', 
           '#1406d1', '#1406d3', '#1606d3', '#1608d4', '#1708d4', '#1708d4', '#1808d6', 
           '#1808d7', '#1908d7', '#1909d8', '#1a09d8', '#1a09d9', '#1b09da', '#1b09da', 
           '#1b09db', '#1b0adc', '#1b0adc', '#1c0add', '#1c0add', '#1e0ade', '#1e0ade', 
           '#1f0bde', '#1f0be0', '#200be0', '#200be1', '#210be1', '#210be1', '#220ce3', 
           '#220ce4', '#230ce4', '#230ce4', '#240ce4', '#240ce6', '#250de7', '#250de7', 
           '#260de7', '#260de9', '#270de9', '#270dea', '#280dea', '#280deb', '#290dec', 
           '#290dec', '#2a0ded', '#2a0dee', '#2b0fee', '#2b0fee', '#2c0fee', '#2c0ff0', 
           '#2d0ff1', '#2d0ff1', '#2e10f1', '#2e10f3', '#2f10f3', '#2f10f4', '#3010f4', 
           '#3010f4', '#3111f6', '#3111f6', '#3111f6', '#3111f7', '#3311f7', '#3311f9', 
           '#3412f9', '#3412fa', '#3512fa', '#3512fa', '#3612fc', '#3612fc', '#3713fc', 
           '#3713fd', '#3713fd', '#3713ff', '#3713ff', '#3713ff', '#3713ff', '#3713ff', 
           '#3718ff', '#361cff', '#3523ff', '#3428ff', '#332dff', '#3131ff', '#3137ff', 
           '#303dff', '#2f42ff', '#2e47ff', '#2d4cff', '#2c51ff', '#2b55ff', '#2a5cff', 
           '#2961ff', '#2866ff', '#276bff', '#2670ff', '#2476ff', '#237aff', '#2280ff', 
           '#2185ff', '#208aff', '#1f90ff', '#1e95ff', '#1c9aff', '#1b9fff', '#1ba4ff', 
           '#1aa9ff', '#19aeff', '#18b4ff', '#17b9ff', '#16beff', '#14c3ff', '#14c9ff', 
           '#13ceff', '#12d3ff', '#12d4ff', '#12d8ff', '#12dbff', '#12deff', '#12e1ff', 
           '#12e3ff', '#12e6ff', '#12e9ff', '#12ecff', '#12eeff', '#12f1ff', '#12f4ff', 
           '#12f6ff', '#12f9ff', '#12fcff', '#12fcff', '#1bfcf6', '#25fcec', '#2efce3', 
           '#37fcd9', '#41fcd0', '#4bfcc6', '#54fcbd', '#5efcb3', '#67fcaa', '#71fca0', 
           '#79fc97', '#84fc8d', '#8dfd84', '#97fd79', '#a0fd71', '#aafd67', '#b3fd5e', 
           '#bdfd54', '#c6fd4b', '#d0fd41', '#d9ff37', '#e3ff2e', '#ecff25', '#f6ff1b', 
           '#ffff12', '#fff712', '#fff012', '#ffe912', '#ffe112', '#ffda12', '#ffd312', 
           '#ffcb12', '#ffc412', '#ffbb12', '#ffb512', '#ffad12', '#ffa612', '#ff9f12', 
           '#ff9712', '#ff9012', '#ff8812', '#ff8112', '#ff7912', '#ff7212', '#ff6b12', 
           '#ff6312', '#ff5c12', '#ff5412', '#ff4d12', '#fc4512', '#fa3d12', '#f63511', 
           '#f42d11', '#f12611', '#ee1e11', '#ec1711', '#ea1010', '#e71017', '#e4101c', 
           '#e11023', '#de0f2a', '#dc0f2f', '#da0f35', '#d70f3b', '#d40f40', '#d10d45', 
           '#ce0d4b', '#cc0d4f', '#ca0d54', '#c70d59', '#c40d5d', '#c10d62', '#be0d66', 
           '#c51e6a', '#cb306f', '#d04377', '#d65780', '#dc6c8b', '#e18298', '#e799a7', 
           '#eeb1b9', '#f3cace', '#f9e4e4', '#ffffff']

SPECS = {
    "lightning_1min_netcdf": lightning_1min_netcdf,
    "time_interval": datetime.timedelta(minutes=data_time_interval_min),
    "lookback_period": datetime.timedelta(minutes=data_lookback_period_min),
    "summation_period": datetime.timedelta(minutes=data_summation_period_min),
    "expiration_time": datetime.timedelta(minutes=data_expiration_min),
    "data_time_interval_timedelta": datetime.timedelta(minutes=data_time_interval_min),
    "data_expiration_timedelta": datetime.timedelta(minutes=data_expiration_min),
    "thredds_catalog_url": thredds_catalog_url,
    "thredds_download_base_url": thredds_download_base_url,
    "input_folder": input_folder,
    "temp_folder": temp_folder,
    "output_folder": output_folder,
    
    "min_lon": min_lon,
    "max_lon": max_lon,
    "min_lat": min_lat,
    "max_lat": max_lat,

    "temp_summation_csv": temp_summation_csv,
    "temp_summation_shp": temp_summation_shp,
    "temp_summation_raster": temp_summation_raster,
    "raw_data_resolution_deg": raw_data_resolution_deg,
    "interpolation_resolution_deg": interpolation_resolution_deg,
    "skip_existing_file_check": skip_existing_file_check,
    #"arcpro_template_file": arcpro_template_file,
    #"arcpro_extent": arcpro_extent,
    #"image_size": image_size,
    "temp_lightning_density_sum_raster_file": temp_lightning_density_sum_raster_file,
    "temp_lightning_density_image_placefile": temp_lightning_density_image_placefile,
    "lightning_density_image_placefile": lightning_density_image_placefile,
    "data_summation_period_min": data_summation_period_min,
    "colors": colors,
}
