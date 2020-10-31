import json
import urllib.request
import time
from bs4 import BeautifulSoup
import pathlib
import dependencies.notify_me as notify_me
import difflib
import threading
import platform
import io
import numpy as np
import os
from xmldiff import main, formatting
import lxml.etree

# ---------------------------------- CUSTOM THREAD DEFINITION FOR CONTINUOUS MONITORING ------------------------------ #


class CustomThread(threading.Thread):

    def __init__(self, path, idx):
        threading.Thread.__init__(self)
        self.path = path
        self.idx = idx
        self.stop = False

    def run(self):
        while not self.stop:
            check_status(self.path, self.idx)


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


def check_status(path, idx):
    # Json load and info storing
    json_info = open(path + '/config.json')
    json_data = json.load(json_info)
    json_info.close()
    website = json_data["websites"][idx]
    email = website["email"]

    # Retrieving website
    html = urllib.request.urlopen(website["url"]).read()

    # Getting the desired element...
    if website["attrib_key"] != 'all':  # One element, defined by "element", "attrib-key", and "attrib_value"
        soup = BeautifulSoup(html, features="lxml")
        element = soup.find(website["element"], {website["attrib_key"]: website["attrib_value"]})
        for jj in range(website["parent_number"]):  # Get parent from element (if desired)
            element = element.parent
    else:  # Or the full HTML
        soup = BeautifulSoup(html, features="lxml")
        element = soup.find('html')
    element = str(element)  # Turn element into a string to compare ir easier with the previous version

    # Load the previous web page versions stored
    files = list(pathlib.Path('data/').glob('*.html'))
    files_name = [file.stem for file in files]
    if not website["name"] in files_name:  # If the HTML file is not already stored, save it
        save_html = io.open("data/" + website["name"] + '.html', "w", encoding="utf-8")
        save_html.write(element)
        save_html.close()
        print("No registers for " + website["name"] + ". Register created\n")
    else:  # Else, read the file
        read_html = io.open("data/" + website["name"] + ".html", "r", encoding="utf-8")
        orig = read_html.read()
        read_html.close()
        # And compare with the new one. Storing the string alters '\n', and '\r', so remove them from both versions when comparing
        if str(element).replace('\n', '').replace('\r', '') != orig.replace('\n', '').replace('\r', ''):  # If the strings are
            # not equal, notificate via console and email
            save_html = io.open("data/" + website["name"] + ".html", "w", encoding="utf-8")  # Save the new web page version
            save_html.write(element)
            save_html.close()
            # Format the differences (old in red, new in green)
            email_body = format_differences(orig.replace('\n', '').replace('\r', ''),
                                            element.replace('\n', '').replace('\r', ''), website["url"])
            notify_me.notify_me(email, website["name"] + ' has changed!', email_body, 'html')  # Send the email
            print(website["name"] + ' has changed!!!\n')
        else:  # Else, just notificate via console
            print('No changes for ' + website["name"] + '...\n')

    # Wait the desired time
    time.sleep(website["refresh_interval"])


# --------------------------------------------------- MAIN FUNCTION -------------------------------------------------- #


# Setting path for Windows and Mac
path = []
if platform.system() == 'Windows':
    path = 'D:/OneDrive - Universidad de Valladolid/Personal/Scripts Utiles/web_monitor'
elif platform.system() == 'Darwin':
    path = '/Users/Vic/OneDrive - Universidad de Valladolid/Personal/Scripts Utiles/web_monitor'

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
        t = CustomThread(path, idx)
        t.start()
        thread_pool.append(t)
        thread_pool_names.append(websites[idx]["name"])

# Infinite loop for adding/removing/activating/deactivating websites
while True:
    # New json version load and info storing. It could have changed or not (we will check it)
    json_info = open(path + '/config.json')
    websites_new = json.load(json_info)["websites"]
    json_info.close()
    websites_new_names = [website['name'] for website in websites_new]

    # If a new website is removed... To check this, make the difference between old names and new names. If something
    # remains, those websites have been removed
    if set(websites_names).difference(websites_new_names) is not None:
        for name in list(set(websites_names).difference(websites_new_names))[::-1]:  # [::-1] reverse the order of the list
            if name in thread_pool_names:  # If the removed website is running, stop it and remove it from the thread pool
                idx = thread_pool_names.index(name)
                thread_pool[idx].stop = True
                del thread_pool[idx]
                del thread_pool_names[idx]
            # Update the website index for the already running threads, because a site has been removed, and it will
            # probably has changed
            idx_update = websites_names.index(name)
            for update in websites_names[idx_update + 1:]:  # Only modify the index of the following threads to the one removed
                if update in thread_pool_names:  # And if the thread is running
                    idx_update2 = thread_pool_names.index(update)
                    thread_pool[idx_update2].idx = thread_pool[idx_update2].idx - 1
            print("Website removed: " + name + "\n")

    # If a new website is added... To check this, make the difference between new names and old names. If something
    # remains, those websites have been added
    if set(websites_new_names).difference(websites_names) is not None:
        for name in list(set(websites_new_names).difference(websites_names))[::-1]:  # [::-1] reverse the order of the list
            # Start it and add it to the thread pool
            idx = websites_new_names.index(name)
            t = CustomThread(path, idx)
            t.start()
            thread_pool.append(t)
            thread_pool_names.append(name)
            print("New website added: " + name + "\n")

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
                idx2 = websites_new_names.index(name)
                t = CustomThread(path, idx2)
                t.start()
                thread_pool.append(t)
                thread_pool_names.append(name)
                print("Re-starting web scrapping for " + name + "\n")
            else:  # If now is inactive (previously was active)
                # Stop it and remove it from the thread pool
                idx2 = thread_pool_names.index(name)
                thread_pool[idx2].stop = True
                del thread_pool[idx2]
                del thread_pool_names[idx2]
                print("Web scrapping for " + name + " has been stopped. Index " + str(idx2) + "\n")

    # Check if there are stored websites that are not currently been in the monitoring list (neither active nor inactive)...
    files = list(pathlib.Path('data/').glob('*.html'))
    for file in files:
        if file.stem not in websites_new_names:  # If so, remove the files. Field "stem" is the name without the suffix
            # (.html in this case)
            print("Removing old files for " + file.stem)
            os.remove(file)

    # Update variables for the next iteration
    websites_names = websites_new_names
    websites = websites_new

    # Run this function every 5000 s
    print("Checking changes in config.json...\n")
    time.sleep(5000)
