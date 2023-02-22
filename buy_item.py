import selenium
from selenium.webdriver.common.by import By


def buy_item(driver, website):

    # Find the desired size, and click
    if website["attrib_key"] == 'id':
        driver.find_element(By.ID, website["attrib_value"]).click()
    elif website["attrib_key"] == 'class':
        driver.find_element(By.CLASS_NAME, website["attrib_value"]).click()
    else:
        error

    driver.find_element(By.XPATH, "//" + website["element"] + "[@" + website["attrib_key"] + "='" + website["attrib_value"] + "']").click()
    driver.find_element(By.XPATH, "//input[@name='username']")

