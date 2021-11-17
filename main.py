import json
import urllib.request
import time
from bs4 import BeautifulSoup
import pathlib
import dependencies.notify_me as notify_me
import threading
import platform
import io
import numpy as np
import os
import shutil
from xmldiff import main, formatting
import lxml.etree
from random import uniform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ---------------------------------- CUSTOM THREAD DEFINITION FOR CONTINUOUS MONITORING ------------------------------ #


class CustomThread(threading.Thread):

    def __init__(self, path, name):
        threading.Thread.__init__(self)
        self.path = path
        self.name = name
        self.stop = False

    def run(self):
        while not self.stop:
            check_status(self.path, self.name)


# ---------------------------------- FUNCTION DEFINITION FOR FORMATTING THE DIFFERENCES ------------------------------ #


def format_differences(old, new, link):

    # ------------------------ FORMAT THE DIFFERENCEs -------------------- #
    xslt = u'''<?xml version="1.0"?>

    <xsl:stylesheet version="1.0"
        xmlns:diff="http://namespaces.shoobx.com/diff"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

        <xsl:template name="mark-diff-insert">
            <ins class="diff-insert">
                <xsl:apply-templates/>
            </ins>
        </xsl:template>

        <xsl:template name="mark-diff-delete">
            <del class="diff-del">
                <xsl:apply-templates/>
            </del>
        </xsl:template>

        <xsl:template name="mark-diff-insert-formatting">
            <span class="diff-insert-formatting">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <xsl:template name="mark-diff-delete-formatting">
            <span class="diff-delete-formatting">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <!-- `diff:insert` and `diff:delete` elements are only placed around
            text. -->
        <xsl:template match="diff:insert">
            <span style="background-color:#82F67C;">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <xsl:template match="diff:delete">
            <span style="background-color:#FF4A4A;">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <!-- If any major paragraph element is inside a diff tag, put the markup
            around the entire paragraph. -->
        <xsl:template match="p|h1|h2|h3|h4|h5|h6">
            <xsl:choose>
                <xsl:when test="ancestor-or-self::*[@diff:insert]">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-insert" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="ancestor-or-self::*[@diff:delete]">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-delete" />
                    </xsl:copy>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:template>

        <!-- Put diff markup in marked paragraph formatting tags. -->
        <xsl:template match="span|b|i|u|sub|sup">
            <xsl:choose>
                <xsl:when test="@diff:insert">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-insert" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="@diff:delete">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-delete" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="@diff:insert-formatting">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-insert-formatting" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="@diff:delete-formatting">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-delete-formatting" />
                    </xsl:copy>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:template>

        <!-- Put diff markup into pseudo-paragraph tags, if they act as paragraph. -->
        <xsl:template match="li|th|td">
            <xsl:variable name="localParas" select="para|h1|h2|h3|h4|h5|h6" />
            <xsl:choose>
                <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:insert]">
                    <xsl:copy>
                        <para>
                            <xsl:call-template name="mark-diff-insert" />
                        </para>
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:delete]">
                    <xsl:copy>
                        <para>
                            <xsl:call-template name="mark-diff-delete" />
                        </para>
                    </xsl:copy>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:template>


        <!-- =====[ Boilerplate ]=============================================== -->

        <!-- Remove all processing information -->
        <xsl:template match="//processing-instruction()" />

        <!-- Catch all with Identity Recursion -->
        <xsl:template match="@*|node()">
            <xsl:copy>
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
        </xsl:template>

        <!-- Main rule for whole document -->
        <xsl:template match="/">
            <xsl:apply-templates/>
        </xsl:template>

    </xsl:stylesheet>'''
    xslt_template = lxml.etree.fromstring(xslt)

    class HTMLFormatter(formatting.XMLFormatter):
        def render(self, result):
            transform = lxml.etree.XSLT(xslt_template)
            result = transform(result)
            return super(HTMLFormatter, self).render(result)

    formatter = HTMLFormatter(text_tags=('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'),
                              formatting_tags=('b', 'u', 'i', 'em', 'super', 'sup', 'sub', 'link', 'a', 'span'))
    result = main.diff_texts(old, new, formatter=formatter)

    # -------------------------- BUILD THE HTML EMAIL BODY ------------------------------ #
    html_code = """\
            <html>
                <head>
                    <meta http-equiv="Content-Type"
                          content="text/html; charset=utf-8" />
                    <style type="text/css">
                        .diff-insert{background-color:#82F67C}
                        .diff-del{background-color:#FF6666}
                        .diff-insert-formatting{background-color:#82F67C}
                        .diff-delete-formatting{background-color:#FF6666}
                    </style>
                </head>
                <body>
                    <a href='""" + link + """'>Visit web page</a>
                    <br><br><br><br>
                    """ + result + """
                    <br><br>
                </body>
            </html>
    """
    return html_code


# ---------------------------------- FUNCTION DEFINITION FOR CHECKING THE CHANGES ------------------------------------ #


def check_status(path, name):
    # Json load and info storing
    json_info = open(path + '/config.json')
    json_data = json.load(json_info)
    json_info.close()
    websites = json_data["websites"]
    websites_names = [website['name'] for website in websites]
    idx = websites_names.index(name)
    website = websites[idx]
    email = website["email"]
    counter_fail = 0

    # Try to retrieve the website. If fails, wait 60 sec and try again. If success, break the infinite loop
    while True:
        try:
            # Retrieving website
            if not website["javascript"]:
                user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
                headers = {'User-Agent': user_agent}

                request = urllib.request.Request(website["url"], None, headers)  # The assembled request
                html = urllib.request.urlopen(request).read()

            else:
                options = Options()
                options.headless = False
                fp = webdriver.FirefoxProfile('./firefox_profile/4obzz88j.web_monitor')
                driver = webdriver.Firefox(fp, options=options, service_log_path=os.devnull)  # service=service

                driver.get(website["url"])
                time.sleep(10)
                html = driver.page_source
                driver.close()

        except Exception as e:
            print(e)
            time.sleep(60)
            continue
        else:
            break

    # Getting the desired element...
    if website["attrib_key"] != 'all':  # One element, defined by "element", "attrib-key", and "attrib_value"
        soup = BeautifulSoup(html, features="lxml")
        if website["attrib_key"] == "text":  # This is for selecting an element by text
            if website["all_elements"]:
                element = soup.find_all(website["element"], text=re.compile('.*' + website["attrib_value"] + '.*'))
            else:
                element = soup.find(website["element"], text=re.compile('.*' + website["attrib_value"] + '.*'))
        else:
            if website["all_elements"]:                element = soup.find_all(website["element"], {website["attrib_key"]: website["attrib_value"]})
            else:
                element = soup.find(website["element"], {website["attrib_key"]: website["attrib_value"]})
        if element is not None and element != "None":
            for jj in range(website["parent_number"]):  # Get parent from element (if desired)
                for kk in range(len(element)):
                    element[kk] = element[kk].parent
        if website["only_text"]:  # This is for assessing the differences only in the text
            for kk in range(len(element)):
                element[kk] = element[kk].get_text()
    else:  # Or the full HTML
        soup = BeautifulSoup(html, features="lxml")
        element = soup.find('html')

    element = str(element)  # Turn element into a string to compare it easier with the previous version

    # Load the previous web page versions stored
    if element is not None and element != "None":
        counter_fail = 0
        files = list(pathlib.Path('data/').glob('*.html'))
        files_name = [file.stem for file in files]
        if not website["name"] in files_name:  # If the HTML file is not already stored, save it
            save_html = io.open("data/" + website["name"] + '.html', "w", encoding="utf-8")
            save_html.write(element)
            save_html.close()
            print("No registers for '" + website["name"] + "'. Register created\n")
        else:  # Else, read the file
            read_html = io.open("data/" + website["name"] + ".html", "r", encoding="utf-8")
            orig = read_html.read()
            read_html.close()
            # And compare with the new one. Storing the string alters '\n', and '\r', so remove them from both versions when comparing
            if str(element).replace('\n', '').replace('\r', '') != orig.replace('\n', '').replace('\r', ''):  # If the strings are
                # not equal, notificate via console and email
                shutil.copy(str(pathlib.Path().resolve()) + '\\data\\' + website["name"] + '.html',
                          str(pathlib.Path().resolve()) + '\\data\\Previous versions\\' + website["name"] + '.html')
                save_html = io.open("data/" + website["name"] + ".html", "w", encoding="utf-8")  # Save the new web page version
                save_html.write(element)
                save_html.close()
                # Format the differences (old in red, new in green)
                if website["compose_body"]:
                    email_body = format_differences(orig.replace('\n', '').replace('\r', ''),
                                                    element.replace('\n', '').replace('\r', ''), website["url"])
                    notify_me.notify_me(email, website["name"] + ' has changed!', email_body, 'html')  # Send the email
                else:
                    email_body = """\
                            <html>
                                <head>
                                    <meta http-equiv="Content-Type"
                                          content="text/html; charset=utf-8" />
                                    <style type="text/css">
                                        .diff-insert{background-color:#82F67C}
                                        .diff-del{background-color:#FF6666}
                                        .diff-insert-formatting{background-color:#82F67C}
                                        .diff-delete-formatting{background-color:#FF6666}
                                    </style>
                                </head>
                                <body>
                                    <a href='""" + website["url"] + """'>Visit web page</a>
                                </body>
                            </html>
                    """
                    notify_me.notify_me(email, website["name"] + ' has changed!', email_body, 'html')  # Send the email

                print("'" + website["name"] + "' has changed!!!\n")
                time.sleep(300)
            else:  # Else, just notificate via console
                print("No changes for '" + website["name"] + "'\n")
    else:
        counter_fail += 1
        if counter_fail == 10:
            notify_me.notify_me(email, website["name"] + ' is broken :(', '', 'html')  # Send the email

        print("The element '" + website["name"] + "' couldn't be found. Retrying\n")

    # Wait the desired time
    time.sleep(website["refresh_interval"])

# --------------------------------------------------- MAIN FUNCTION -------------------------------------------------- #

# Setting path for Windows and Mac
path = []
if platform.system() == 'Windows':
    path = 'D:/OneDrive - gib.tel.uva.es/Personal/Scripts Utiles/web_monitor'
elif platform.system() == 'Darwin':
    path = '/Users/Vic/OneDrive - gib.tel.uva.es/Personal/Scripts Utiles/web_monitor'

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
        time.sleep(round(uniform(5, 15), 2)) # Wait a random amount of time (between 5 and 50 seconds) before starting another thread to avoid trying to send two mails at a time

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
    files = list(set(pathlib.Path('data/').glob('*.html')) - set(pathlib.Path('data/').glob('OLD - *.html')))
    for file in files:
        if file.stem not in thread_pool_names:  # If so, remove the files. Field "stem" is the name without the suffix
            # (.html in this case)
            print("Removing file of '" + file.stem + "'\n")
            os.remove(file)
            try:
                os.remove(str(pathlib.Path().resolve()) + '\\data\\Previous versions\\' + file.stem + '.html')
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
    time.sleep(300)
