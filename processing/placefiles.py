import matplotlib.pyplot as plt
import matplotlib.colors as colors

def plot_lightning(lons, lats, values, filename, **kwargs):
    """

    Plot data and output .png image for display in GR.

    Parameters:
    -----------
    lons: array-like
        2-d array of projected longitude values

    lats: array-like
        2-d array of projected latitude values

    values: array-like
        2-d array of values to be plotted (i.e. summed lightning)

    filename: string
        Output filename

    **kwargs: dict
        Dictionary containing output specifications (passed from configs.py file)

    Returns:
    --------
    min/max latitude and logitudes of plot along with midpoints

    Output:
    -------
    PNG of values array plotted over the limited domain specified in configs.py

    """
    
    fig = plt.figure(dpi=250, frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])

    # If using alpha, may need to set antialiased=False
    ax.pcolor(lons, lats, values, 
              norm=colors.PowerNorm(gamma=0.22, vmin=0, vmax=256),
              cmap=colors.ListedColormap(kwargs.get("colors")))
    
    # Instead of plotting geographic overlays (needing a shapefile read), plot a few
    # radar sites to see if they match up when the image is loaded into GR. 
    #ax.scatter(-88.0849, 41.604, s=10, c='red') #LOT
    #ax.scatter(-91.191, 43.82296, s=10, c='red') #ARX
    #ax.scatter(-93.72364, 41.731167, s=10, c='red') #DMX
    #ax.scatter(-89.337, 40.15, s=10, c='red') #ILX
    #ax.scatter(-90.58, 41.61, s=10, c='red') #DVN
    #ax.scatter(-88.55, 42.97, s=10, c='red') #MKX
    #ax.scatter(-85.70, 41.36, s=10, c='red') #IWX
    #ax.scatter(-85.55, 42.89, s=10, c='red') #GRR
    #ax.scatter(-86.30, 39.70, s=10, c='red') #IND
    #ax.scatter(-97.302, 32.573, s=10, c='red') #FWS
    #ax.scatter(-97.383, 30.722, s=10, c='red') #GRK
    
    ax.set_xlim(kwargs.get('min_lon'), kwargs.get('max_lon'))
    ax.set_ylim(kwargs.get('min_lat'), kwargs.get('max_lat'))
    min_lat_image, max_lat_image = ax.get_ylim()
    min_lon_image, max_lon_image = ax.get_xlim()
    mid_lat_image = (min_lat_image + max_lat_image)/2.
    mid_lon_image = (min_lon_image + max_lon_image)/2.

    # Likely some of this is redundant, but can't totally figure out how to ensure
    # edges are trimmed from all graphics. Best to leave this alone, eh?
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close('all')

    return (min_lat_image, max_lat_image, min_lon_image, max_lon_image, mid_lat_image,
            mid_lon_image)
    

def write_lightning_img(png_file, file_date, most_recent_file_date, image_info,
                        is_first_image, is_final_image, **kwargs):
    lightning_density_placefile = kwargs.get("temp_lightning_density_image_placefile")
    data_interval_timedelta = kwargs.get("data_time_interval_timedelta")
    data_expiration_timedelta = kwargs.get("data_expiration_timedelta")
    summation_period_min = kwargs.get("data_summation_period_min")

    min_lat_image, max_lat_image, min_lon_image, max_lon_image, mid_lat_image, \
    mid_lon_image = image_info

    png_file = png_file[len(kwargs.get("output_folder")):]
    if is_first_image:
        placefile_f = open(lightning_density_placefile,"w")
        title_date_string = most_recent_file_date.strftime("%Y-%m-%d %H%M UTC")
        timerange_start = file_date
        timerange_end = file_date + data_interval_timedelta
        timerange_date_string = timerange_start.strftime("%Y-%m-%dT%H:%M:00Z ") + timerange_end.strftime("%Y-%m-%dT%H:%M:00Z")                    
        placefile_f.write("Title: GLM Lightning " + str(summation_period_min) + "-min Flash Density Images (" + title_date_string + ")\n")
        placefile_f.write("RefreshSeconds: 5\n")
        placefile_f.write("\n")
        placefile_f.write("TimeRange: " + timerange_date_string + "\n")
        placefile_f.write("Image: " + png_file + "\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(min_lon_image) + ", 0, 0\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(min_lon_image) + ", 0, 1\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(min_lon_image) + ", 0, 0\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(max_lon_image) + ", 1, 0\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(max_lon_image) + ", 1, 0\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(max_lon_image) + ", 1, 1\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(max_lon_image) + ", 1, 1\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(min_lon_image) + ", 0, 1\n")
        placefile_f.write("End:")
    elif is_final_image:
        placefile_f = open(lightning_density_placefile,"a")
        timerange_start = file_date
        timerange_end = file_date + data_expiration_timedelta
        timerange_date_string = timerange_start.strftime("%Y-%m-%dT%H:%M:00Z ") + timerange_end.strftime("%Y-%m-%dT%H:%M:00Z")
        placefile_f.write("\n")
        placefile_f.write("TimeRange: " + timerange_date_string + "\n")
        placefile_f.write("Image: " + png_file + "\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(min_lon_image) + ", 0, 0\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(min_lon_image) + ", 0, 1\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(min_lon_image) + ", 0, 0\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(max_lon_image) + ", 1, 0\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(max_lon_image) + ", 1, 0\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(max_lon_image) + ", 1, 1\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(max_lon_image) + ", 1, 1\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(min_lon_image) + ", 0, 1\n")
        placefile_f.write("End:")      
    else:
        placefile_f = open(lightning_density_placefile,"a")
        timerange_start = file_date
        timerange_end = file_date + data_interval_timedelta
        timerange_date_string = timerange_start.strftime("%Y-%m-%dT%H:%M:00Z ") + timerange_end.strftime("%Y-%m-%dT%H:%M:00Z")
        placefile_f.write("\n")
        placefile_f.write("TimeRange: " + timerange_date_string + "\n")
        placefile_f.write("Image: " + png_file + "\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(min_lon_image) + ", 0, 0\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(min_lon_image) + ", 0, 1\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(min_lon_image) + ", 0, 0\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(max_lon_image) + ", 1, 0\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(max_lat_image) + ", " + str(max_lon_image) + ", 1, 0\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(max_lon_image) + ", 1, 1\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(max_lon_image) + ", 1, 1\n")
        placefile_f.write(" " + str(mid_lat_image) + ", " + str(mid_lon_image) + ", 0.5, 0.5\n")
        placefile_f.write(" " + str(min_lat_image) + ", " + str(min_lon_image) + ", 0, 1\n")
        placefile_f.write("End:")

    placefile_f.close()
    del placefile_f
