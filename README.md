**NOTES**: 
* **IMPORTANT**: A Firefox installation is required
* If you want to track in Zara a product with multiple colors, you should use "web_monitor_Zara" script (as a direct link to the specific color is needed). Else you could try to seek the product in the app and use the "Share" function, where you will probably obtain the direct link to the specific color you want to track, thus being to use this script
* To know the element type and its attribute and key to identify it, you should inspect the element you want to monitor it with a web browser. Example: 
     1) Go to the website you want to track, 
     2) identify visually the element you want to track, 
     3) inspect it (with Google Chrome right click+inspect element), 
     4) seek for the concrete element you want to track, and extract the "element", "attrib_key" and "attrib_value" of the element you want to track 
 
 
In the json file...
* **"url"**: url to be checked
* **"element"**: element type to be checked
* **"attrib_key"**: attribute key that identifies unequivocally "element". If you want to get an element by its text use "text"
* **"attrib_value"**: attribute value that identifies unequivocally "element"
* **"parent_number"**: if you can't identify unequivocally your element, identify a child, and indicate in this how many child-parent jumps are necessary to reach from the identified element to your desired element
* **"refresh_interval"**: checking interval (in seconds). For elements with "javascript" set to "true", this time will be increased by 10 seconds due to Selenium issues
* **"name"**: identifier. MUST BE UNIQUE
* **"active"**: true/false, to activate/deactivate the monitoring
* **"email"**: email address to send the notification
* **"javascript"**: true/false, true if the website require javascript
* **"compose_body"**: true/false, true if you want to send the changes in the email body, if not only the link will be sent
* **"only_text"**: true/false, true if you want to check only the text from the selected element

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
	"only_text": false
}
```