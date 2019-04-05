from   selenium import webdriver
from   selenium.common.exceptions import TimeoutException
from AUTH import ucsdsso
import time
driver = webdriver.Firefox()





driver.get("https://hdh.ucsd.edu/housing/roomselection/pages/index.html")
  
navButton = driver.find_element_by_class_name("buttonlink")
print(navButton)

navButton.click()
time.sleep(2)

driver.get("https://a5.ucsd.edu/tritON/profile/SAML2/Redirect/SSO?execution=e1s1")
pid = driver.find_element_by_id("ssousername")
password = driver.find_element_by_id("ssopassword")

pid.send_keys(ucsdsso["pid"])
password.send_keys(ucsdsso["password"])
login_button = driver.find_element_by_name("_eventId_proceed")
login_button.click()    
time.sleep(2)
print(driver.current_url)

room_selection_link = driver.find_element_by_link_text("2019 Room Selection: Eligibility, Contract, Prepayment and Lottery Time & Checklist")
room_selection_link.click()
print(driver.current_url)

room_selection_sixth = driver.find_element_by_xpath('//*[@rmscomponentid="11856"]')
print(room_selection_sixth)
room_selection_sixth.click()

vacancy_viewer = room_selection_sixth = driver.find_element_by_xpath('//*[@rmscomponentid="11831"]')
vacancy_viewer.click()

nav_button_next = driver.find_element_by_id('NavButtonNext')
nav_button_next.click()

time.sleep(2)

apartments = driver.find_elements_by_xpath('//*[@rmssellevel="Building"]')
print(apartments)
for building in apartments:
    if building != driver.find_element_by_id('ELAIDBuilding'):
        building.click()
  
driver.current_url

