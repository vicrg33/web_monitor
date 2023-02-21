**NOTES**: 
* **IMPORTANT**: A Chrome installation is required
* If you want to track in Zara a product with multiple colors, you should use "web_monitor_Zara" script (as a direct link to the specific color is needed). Else you could try to seek the product in the app and use the "Share" function, where you will probably obtain the direct link to the specific color you want to track, thus being to use this script
* To know the element type and its attribute and key to identify it, you should inspect the element you want to monitor it with a web browser. Example: 
     1) Go to the website you want to track, 
     2) identify visually the element you want to track, 
     3) inspect it (with Google Chrome right click+inspect element), 
     4) seek for the concrete element you want to track, and extract the "element", "attrib_key" and "attrib_value" of the element you want to track 
* The web monitor may continue checking (and storing) a website just after the deactivation of the website. Not sure of why is this happening (a kind of desynchronization?), but it is not a problem, as in the next iteration of the main script it will automatically be fixed, i.e., this unwanted behaviour will only last one iteration of the main script. 
 
In the json file...
* **"url"**: url to be checked
* **"element"**: element type to be checked
* **"attrib_key"**: attribute key that identifies unequivocally "element". If you want to get an element by its text use "text". If you want to search by xpath put "xpath" here and the xpath in "attrib_value", in that case the content of "element" field does not matter. If empty (this and "attrib_value") an element "element" with no attributes will be searched
* **"attrib_value"**: attribute value that identifies unequivocally "element"
* **"parent_number"**: if you can't identify unequivocally your element, identify a child, and indicate in this how many child-parent jumps are necessary to reach from the identified element to your desired element
* **"refresh_interval"**: checking interval (in seconds). Do not use values less than 20 to avoid problems for elements using "javascript". Also, in elements using "javascript", the "refresh_interval" will be increased by 10 seconds due to Selenium operation
* **"name"**: identifier. MUST BE UNIQUE
* **"active"**: true/false, to activate/deactivate the monitoring
* **"email"**: email address to send the notification
* **"javascript"**: true/false, true if the website require javascript
* **"compose_body"**: true/false, true if you want to send the changes in the email body, if not only the link will be sent. Recomended false, as it provokes many errors
* **"only_text"**: true/false, true if you want to check only the text from the selected element
* **"all_elements"**: true/false, true if you want to check all the elements that match attrib_key-attrib_value, false if only the "idx_element" match
* **"idx_element"**: int, the index of the element (that match attrib_key-attrib_value) that will be tracked. Will only be used if "all_elements" is false
* **"only_check_attribute"**: true/false, to check only the value of one attribute of the selected element
* **"attribute_to_check"**: the name of the attribute to check for changes
* **"login_needed"**: true/false, to work with websites that require a login. If true, browser metadata will be created to store login information (when deactivated it will automatically be deleted). To monitor this type of websites you have to: i) deactivate the headless mode, ii) start the web monitor program and pause the script when the browser is opened **FOR THE WEBSITE THAT REQUIRES LOGIN**, iii) log in to the website, iv) stop the web monitor program, v) activate headless mode, and vi) all done! you can start the web monitor program normally. 

**EXAMPLE**
```sh
{
    "url": "https://www.unileon.es/actualidad/convocatorias-urgentes",
    "element": "div",
    "attrib_key": "class",
    "attrib_value": "view-content",
    "parent_number": 0,
    "refresh_interval": 86400,
    "name": "Universidad de Leon - Convocatorias urgentes",
    "active": true,
    "email" : "patriarce15@gmail.com",
    "javascript" : false,
    "compose_body": true,
    "only_text": false,
    "all_elements": false,
    "idx_element": 1,
    "only_check_attribute": true,
    "attribute_to_check": "id",
    "login_needed": false
},
```