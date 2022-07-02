import os
import logging
from configs import current_folder

def logfile(logname):
    """
    Initiate a logging instance and pass back for writing to the file system.

    """
    #if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
    logging.basicConfig(filename="%s/%s.log" % (current_folder, logname),
                        format='%(levelname)s %(asctime)s :: %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S")
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    return log
