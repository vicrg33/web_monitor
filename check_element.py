import pathlib
import io
import shutil

import buy_item
import dependencies.notify_me as notify_me
import dependencies.telegram_notify as telegram_notify
from dependencies.get_email_body import simple_body
import time


def check_element(path, element, website, counter_fail, email, driver=[]):  # This will compare element with the stored element, if it does
    # not exist store it...
    # Load the previous web page versions stored
    if element is not None and element != "None":
        counter_fail = 0  # The site has been properly get, so set the counter to 0
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

                if website["double_check"]:
                    if not 'COUNTER_' + website["name"].replace(" ", "_") in globals():
                        globals()['COUNTER_' + website["name"].replace(" ", "_")] = True
                        print("'" + website["name"] + "' has changed. We will check once again before notifying...\n")
                        return
                    else:
                        del globals()['COUNTER_' + website["name"].replace(" ", "_")]

                # Notify
                email_body = simple_body(website["url"])
                notify_me.notify_me(email, website["name"] + ' has changed!', email_body, 'html')  # Send the email
                telegram_notify.telegram_notify(website["name"] + ' has changed! Link: ' + website["url"])  # Send a Telegram message

                # # Buy the item (only in zara sites)
                # try:
                #     if website["do_buy"]:
                #         buy_item.buy_item(driver, website)
                # except Exception as err_buy_item:
                #     print("Could not buy the item: " + str(err_buy_item) + "\n")

                # Move the previous version to the "Previous versions" folder, and the new to "data" folder
                shutil.copy(path + '/data/' + website["name"] + '.html',
                          path + '/data/Previous versions/' + website["name"] + '.html')
                save_html = io.open("data/" + website["name"] + ".html", "w", encoding="utf-8")  # Save the new web page version
                save_html.write(element)
                save_html.close()

                print("'" + website["name"] + "' has changed!!!\n")
                # time.sleep(300)
            else:  # Else, just notificate via console

                if 'COUNTER_' + website["name"].replace(" ", "_") in globals():
                    del globals()['COUNTER_' + website["name"].replace(" ", "_")]

                print("No changes for '" + website["name"] + "'\n")
                a = 0
    else:
          print("The element '" + website["name"] + "' couldn't be found. Retrying\n")
