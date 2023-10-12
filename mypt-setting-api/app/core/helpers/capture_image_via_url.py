from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
import time
   
def capturer_as_base64(url, size=[0, 0]):
    try:
        fpt_proxy = "http://proxy.hcm.fpt.vn:80"
        
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--proxy-server=%s' % fpt_proxy)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument("--remote-debugging-port=9222")
        # chrome_options.add_argument("--virtual-time-budget=15000")
        chrome_options.binary_location = "/usr/bin/google-chrome"
 
        # "/usr/local/share/chromedriver"
        # "C:/Users/84962/Downloads/chromedriver"
        driver = webdriver.Chrome("/usr/local/share/chromedriver", chrome_options=chrome_options)
        if size is [0, 0]:
            driver.set_window_size(1920, 1200)
        else:
            driver.set_window_size(size[0], size[1])
            
        driver.get(url)
        driver.implicitly_wait(40)
        timeout = 40
        try:
            element_present = EC.presence_of_element_located((By.ID, "Element_to_be_found"))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

        c = driver.get_screenshot_as_base64()
        driver.quit()
        return c, "success"
    except Exception as e:
        print(e)
        driver.quit()
        return False, str(e)
