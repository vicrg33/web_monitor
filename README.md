**NOTES**: 
* If you want to add a new site, ALWAYS add it at the end of the json file.
 * To know the element type and its attribute and key to identify it, you should inspect the element you want to monitor it with a web browser. Example: 
     1) Go to the website you want to track, 
     2) identify visually the element you want to track, 
     3) inspect it (with Google Chrome right click+inspect element), 
     4) seek for the concrete element you want to track, and extract "element", "attrib_key" and "attrib_value" from the source code of the element you want to track 
 
 
In the json file...
* **"url"**: url to be checked,
* **"element"**: element type to be checked,
* **"attrib_key"**: attribute key that identifies unequivocally "element",
* **"attrib_value"**: attribute value that identifies unequivocally "element",
* **"parent_number"**: if you can't identify unequivocally your element, identify a child, and indicate in this how many child-parent jumps are necessary to reach from the identified element to your desired element,
* **"refresh_interval"**: checking interval (in seconds),
* **"name"**: identifier. MUST BE UNIQUE,
* **"active"**: true/false, to activate/deactivate the monitoring
    
**EXAMPLE**
```sh
{
    "url": "https://sede.uva.es/opencms/opencms/es/Tablones/Tablon_de_Anuncios/RESOLUCIONES_ORGANOS_UNIPERSONALES/index.html?page=1",
    "element": "div",
    "attrib_key": "class",
    "attrib_value": "contenido",
    "parent_number": 0,
    "refresh_interval": 3600,
    "name": "UVa-Ayudas",
    "active": false
}
```