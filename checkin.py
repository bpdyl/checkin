
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


LIS_URL = "http://login.lisnepal.com.np/{}"

def get_driver():
  chrome_options=Options()
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--headless")
  chrome_options.add_argument('-disable-dev-shn-usage')
  wd = webdriver.Chrome(options=chrome_options)
  return wd



class CheckInBot:
    def __init__(self) -> None:
        self.__driver = get_driver()
        self.__driver.get(LIS_URL.format('home/login_outside'))

    def login(self, login_details, max_retries = 3):
        WebDriverWait(self.__driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "common-box")))

        ##Entering the username 
        username_input = self.__driver.find_element(By.ID,"usr-name")
        username_input.send_keys(login_details['username'])

        ##Entering the password 
        password_input = self.__driver.find_element(By.ID,"usr-password")
        password_input.send_keys(login_details['password'])

        login_btn = self.__driver.find_element(By.NAME,"submit")
        login_btn.click()

        self.__driver.implicitly_wait(5)
        logger.info(f"Signed up successful for {login_details['alias']}")
        print(f"Signed up successful for {login_details['alias']}")

    def checkin_or_checkout(self):
        self.__driver.get(LIS_URL.format('home'))
        checkout_btn = self.__driver.find_element(By.ID,'check_out')
        checkin_btn = self.__driver.find_element(By.ID,"check_in")
        if checkin_btn:
            print("Check in button found")
        elif checkout_btn:
            print("Checkout button found")

    def checkin(self):
        self.__driver.get(LIS_URL.format('home'))
        try:
            checkin_btn = self.__driver.find_element(By.ID,'check_in ')
            checkin_btn.click()
        except Exception as e:
            print("No element is found",e)


    def checkout(self):
        self.__driver.get(LIS_URL.format('home'))
        try:
            checkout_btn = self.__driver.find_element(By.ID,'check_out')
            print(checkout_btn)
            checkout_btn.click()
            WebDriverWait(self.__driver, 5).until(EC.alert_is_present())

            # Store the alert in a variable for reuse
            alert = self.__driver.switch_to.alert

            # Store the alert text in a variable
            text = alert.text

            # Press the Cancel button
            alert.accept()
        except Exception as e:
            print("No checkout element is found",e)

        
