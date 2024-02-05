import json
import time
import urllib.request
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import re
import check_element
import os
from bs4 import BeautifulSoup


def check_status(path, path_gecko_metadata, name, driver, iteration_wait):
    # Json load and info storing
    json_info = open(path + '/config.json')
    json_data = json.load(json_info)
    json_info.close()
    websites = json_data["websites"]
    websites_names = [website['name'] for website in websites]
    # If the website could not be found, wait to allow the main script to remove it
    try:
        idx = websites_names.index(name)
        website = websites[idx]
    except:
        print("Website not detected. Waiting until the next load of the configuration file\n")
        time.sleep(iteration_wait * 1.5)
        return
    email = website["email"]
    counter_fail = 0

    if not driver:
        # Try to retrieve the website. If fails, wait 60 sec and try again. If success, break the infinite loop
        while True:
            try:
                # Retrieving website
                options = Options()
                options.add_argument('--headless')
                options.add_argument("--window-size=1920x1080")  # Required by the "find by XPath" functionality
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference("useAutomationExtension", False)
                user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
                options.add_argument('user-agent={0}'.format(user_agent))
                options.add_argument("--disable-gpu")
                if website["login_needed"]:
                    if not os.path.exists(path_gecko_metadata + '/gecko_tmp/' + website["name"]):
                        os.mkdir(path_gecko_metadata + '/gecko_tmp/' + website["name"])
                    options.add_argument(
                        "user-data-dir=" + path_gecko_metadata + "/gecko_tmp/" + website["name"])
                # service = Service('chromedriver.exe', log_path=os.devnull)
                driver = webdriver.Firefox(options=options, service=Service(GeckoDriverManager().install()))
                driver.implicitly_wait(90) # Set a timeout for loading the page, after 90s it will return an error

                driver.get(website["url"])
                time.sleep(website["waiting_time"] + 10)

                if website["attrib_key"] == "xpath":
                    time.sleep(5)
                    driver_element = driver.find_element(By.XPATH, website["attrib_value"])
                    if website["only_check_attribute"]:  # To check only the value of an attribute
                        html = driver_element.get_attribute(website["attribute_to_check"])
                    else:
                        html = driver_element.get_attribute('outerHTML')
                    # driver.close()
                    # driver.quit()
                else:
                    html = driver.page_source
                    # driver.close()
                    # driver.quit()
            except Exception as e:
                print('Failed to initiate the driver. Retrying...')
                print(str(e))
                print('\n')
                time.sleep(20)
                continue
            else:
                break
    else:
        try:
            # Retrieving website
            driver.get(website["url"])

            # Wait for the website to be loaded
            if website["waiting_time"] > 0:
                time.sleep(website["waiting_time"])

            if website["attrib_key"] == "xpath":
                time.sleep(5)
                try:
                    driver_element = driver.find_element(By.XPATH, website["attrib_value"])
                except Exception:
                    print("WARNING! The website " + website["name"] + " has failed (couldn't get the XPATH). Retrying...\n")
                    time.sleep(website["refresh_interval"])
                    return
                if website["only_check_attribute"]:  # To check only the value of an attribute
                    html = driver_element.get_attribute(website["attribute_to_check"])
                else:
                    html = driver_element.get_attribute('outerHTML')
                # driver.close()
                # driver.quit()
            else:
                html = driver.page_source
        except Exception:
            print("WARNING! The website " + website["name"] + " has failed (couldn't get the page source). Retrying...\n")
            time.sleep(website["refresh_interval"])
            return


    # Getting the desired element...
    if website["attrib_key"] != 'all' and not website["attrib_key"] == "xpath": # One element, defined by "element", "attrib-key", and "attrib_value"
        soup = BeautifulSoup(html, features="lxml")
        if website["attrib_key"] == "text":  # This is for selecting an element by text
            element = soup.find_all(website["element"], text=re.compile('.*' + website["attrib_value"] + '.*'))
            if not website["all_elements"]:  # Check all the elements that match
                element = element[website["idx_element"]]
        else:
            element = soup.find_all(website["element"], {website["attrib_key"]: website["attrib_value"]})
            if not website["all_elements"]:  # Check all the elements that match
                try:
                    element = element[website["idx_element"]]
                except Exception:
                    # This Exception handles the case when the element cannot be obtained. The object will be retrieved
                    # again and again, so I will inform it in the command line
                    print("WARNING! The website " + website["name"] + " has failed (couldn't get the element). Retrying...\n")
                    time.sleep(website["refresh_interval"])
                    return

        if website["only_check_attribute"]:  # To check only the value of an attribute. In this case, look for parents,
            # and check only text does not make sense, so "check_element" will be called independently for this condition
            try:  # Get the element desired attribute. This could be a bit difficult, so this nested try/Except are required
                element = element.get(website["attribute_to_check"])
                element = str(element)  # Turn element into a string to compare it easier with the previous version
                check_element.check_element(path, element, website, counter_fail, email)  # Check differences in the element
                time.sleep(website["refresh_interval"])
                return
            except Exception:
                try:
                    element = element[0].get(website["attribute_to_check"])
                    element = str(element)  # Turn element into a string to compare it easier with the previous version
                    check_element.check_element(path, element, website, counter_fail, email)  # Check differences in the element
                    time.sleep(website["refresh_interval"])
                    return
                except Exception:  # This Exception catches the case when a ResultSet is returned. It is assumed that
                    # the attribute cannot be obtained. The notification will be sent, as "element" will contain more
                    # stuff than only the attribute to be checked
                    element = str(element)  # Turn element into a string to compare it easier with the previous version
                    check_element.check_element(path, element, website, counter_fail, email)  # Check differences in the element
                    time.sleep(website["refresh_interval"])
                    return

        if element is not None and element != "None":
            if len(element) > 1:  # If there are more than one element...
                for jj in range(website["parent_number"]):  # Get parent from element (if desired)
                    for kk in range(len(element)):
                        element[kk] = element[kk].parent
            else:  # If there is only one...
                for jj in range(website["parent_number"]):  # Get parent from element (if desired)
                    try:
                        element = element[0].parent
                    except:
                        element = element.parent

        if website["only_text"]:  # This is for assessing the differences only in the text
            for kk in range(len(element)):
                element[kk] = element[kk].get_text()

    else:  # Or the full HTML
        soup = BeautifulSoup(html, features="lxml")
        element = soup.find('html')

    element = str(element)  # Turn element into a string to compare it easier with the previous version
    check_element.check_element(path, element, website, counter_fail, email)  # Check differences in the element

    # Wait the desired time
    time.sleep(website["refresh_interval"])

    return driver