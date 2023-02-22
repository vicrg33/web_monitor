import json
import time
import pathlib
import dependencies.set_rw as set_rw
import threading
import platform
import numpy as np
import os
import shutil
from random import uniform
import check_status


# ------------------------------------------------------ PARAMETERS -------------------------------------------------- #

# Setting path for Windows and Mac
path = []
if platform.system() == 'Windows':
    path = 'D:/OneDrive - UVa/Personal/Scripts Utiles/web_monitor'
elif platform.system() == 'Darwin':
    path = '/Users/Vic/OneDrive - UVa/Personal/Scripts Utiles/web_monitor'
iteration_wait = 300  # Time to wait between iterations of the main script (i.e., between two Json-loads)
path_chrome_metadata = 'D:/WebMonitorMetadata/'


# ---------------------------------- CUSTOM THREAD DEFINITION FOR CONTINUOUS MONITORING ------------------------------ #

class CustomThread(threading.Thread):

    def __init__(self, path, name):
        threading.Thread.__init__(self)
        self.path = path
        self.name = name
        self.stop = False

    def run(self):
        driver = []
        while not self.stop:
            driver = check_status.check_status(self.path, path_chrome_metadata, self.name, driver, iteration_wait)


# --------------------------------------------------- MAIN FUNCTION -------------------------------------------------- #

# Initial json load and info storing
json_info = open(path + '/config.json')
websites = json.load(json_info)["websites"]
json_info.close()
websites_names = [website['name'] for website in websites]  # Needed for comparisons with next versions of the json file

# Starting threads for all websites
thread_pool = list()
thread_pool_names = list()
print("Starting the web scrapping application: checking {} websites\n".format(sum([website['active'] for website in
                                                                                   websites])))
for idx in range(len(websites)):
    if websites[idx]["active"]:  # If field active is true... Start the monitoring
        t = CustomThread(path, websites[idx]["name"])
        t.start()
        thread_pool.append(t)
        thread_pool_names.append(websites[idx]["name"])
        time.sleep(round(uniform(5, 15), 2))  # Wait a random amount of time (between 5 and 50 seconds) before starting another thread to avoid trying to send two mails at a time

# Infinite loop for adding/removing/activating/deactivating websites
while True:
    # New json version load and info storing. It could have changed or not (we will check it)
    json_info = open(path + '/config.json')
    websites_new = json.load(json_info)["websites"]
    json_info.close()
    websites_new_names = [website['name'] for website in websites_new]

    # If a website is removed... To check this, make the difference between old names and new names. If something
    # remains, those websites have been removed
    if set(websites_names).difference(websites_new_names) is not None:
        for name in list(set(websites_names).difference(websites_new_names))[::-1]:  # [::-1] reverse the order of the
            # list. Not sure if needed, in previous versions was, but I keep it just in case
            if name in thread_pool_names:  # If the removed website is running, stop it and remove it from the thread pool
                idx = thread_pool_names.index(name)
                thread_pool[idx].stop = True
                del thread_pool[idx]
                del thread_pool_names[idx]
            print("Website removed: '" + name + "'\n")

    # If a website is activated/deactivated...
    websites_names_intersection = list(set(websites_names).intersection(websites_new_names))  # Common websites in old and new version
    websites_xor = []
    websites_new_xor = []
    for name in websites_names_intersection:  # Get the "active" vectors for the common websites, for both old and new version
        idx = websites_names.index(name)
        websites_xor.append(websites[idx]["active"])
        idx = websites_new_names.index(name)
        websites_new_xor.append(websites_new[idx]["active"])
    change = np.bitwise_xor(websites_xor, websites_new_xor)  # Which websites have changed their activation state
    # between old and new version
    for idx in range(len(change)):
        if change[idx]:  # For all the websites that have changed their activation state...
            name = websites_names_intersection[idx]
            if websites_new_xor[idx]:  # If now is active (previously was inactive)
                # Start it and add it to the thread pool
                t = CustomThread(path, name)
                t.start()
                thread_pool.append(t)
                thread_pool_names.append(name)
                print("Re-starting web scrapping for '" + name + "'\n")
            else:  # If now is inactive (previously was active)
                # Stop it and remove it from the thread pool
                idx2 = thread_pool_names.index(name)
                thread_pool[idx2].stop = True
                del thread_pool[idx2]
                del thread_pool_names[idx2]
                print("Web scrapping for '" + name + "' has been stopped\n")

    # Check if there are stored websites that are not currently in the monitoring list (neither active nor inactive)...
    files = list(set(pathlib.Path('data/').glob('*.html')))
    for file in files:
        if file.stem not in thread_pool_names:  # If so, remove the files. Field "stem" is the name without the suffix
            # (.html in this case)
            print("Removing files from '" + file.stem + "'\n")
            os.remove(file)
            try:
                os.remove(path + '/data/Previous versions/' + file.stem + '.html')
            except Exception:
                pass

    # Check if there are stored browser metadata that are not currently in the monitoring list (neither active nor
    # inactive)...
    folders = list(set(pathlib.Path(path_chrome_metadata + 'chrome_tmp/').glob('*/')))
    for folder in folders:
        if folder.stem not in thread_pool_names:  # If so, remove the files
            try:
                shutil.rmtree(path_chrome_metadata + '/chrome_tmp/' + file.stem, onerror=set_rw.set_rw)
                print("Removing browser metadata of '" + file.stem + "'\n")
            except Exception:
                pass

    # If a new website is added... To check this, make the difference between new names and old names. If something
    # remains, those websites have been added
    if set(websites_new_names).difference(websites_names) is not None:
        for name in list(set(websites_new_names).difference(websites_names))[::-1]:  # [::-1] reverse the order of the
            # list. Not sure if needed, in previous versions was, but I keep it just in case
            # Start it and add it to the thread pool
            t = CustomThread(path, name)
            t.start()
            thread_pool.append(t)
            thread_pool_names.append(name)
            print("New website added: '" + name + "'\n")

    # Update variables for the next iteration
    websites_names = websites_new_names
    websites = websites_new

    # Run this function every 900 s. NOTE: This is not the refreshing time for each site (that is indicated in
    # config.json). This indicates how often config.json is loaded looking for changes
    # print("Checking changes in the configuration file")
    time.sleep(iteration_wait)
