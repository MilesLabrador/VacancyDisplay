from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from AUTH import ucsdsso
import time
from bs4 import BeautifulSoup
from datascience import *
import numpy as np
from datetime import datetime
import pandas as pd
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver

profile = FirefoxProfile()
profile.set_preference('browser.cache.disk.enable', False)
profile.set_preference('browser.cache.memory.enable', False)
profile.set_preference('browser.cache.offline.enable', False)
profile.set_preference("network.http.use-cache", False)
profile.set_preference('network.cookie.cookieBehavior', 1)



def available_dissect(room_availability):
        return int(room_availability.replace('(', '').replace(')','').replace('available',''))
def room_type_dissect(room_type):
    if 'single' in room_type.lower():
        return 'single'
    elif 'double' in room_type.lower():
        return 'double'
    elif 'triple' in room_type.lower():
        return 'triple'
    elif 'occupied' in room_type.lower():
        return 'none'

def suite_name_dissect(suite_id):
    parts = suite_id.split('-')
    #print(suite_id)
    if 'MTH' in parts[0].upper():
        floor = None
        apartment_building = parts[0]+'-'+'00'
    else:
        floor = parts[1][2]
        apartment_building = parts[0]+'-'+parts[1][0:2]+'00'
    return (floor, apartment_building)


driver = webdriver.Firefox(firefox_profile=profile)

driver.get("https://hdh2.ucsd.edu/ssoStudent/rmsportal/Home/R") #Link to room selection portal, will prompt us with a login page
driver.implicitly_wait(10) #Make sure that the login page worked by waiting for elements to load for up to 10 seconds

pid = driver.find_element_by_id("ssousername")
password = driver.find_element_by_id("ssopassword")

pid.send_keys(ucsdsso["pid"]) #Send username and password keys to fill-in boxes of login screen
password.send_keys(ucsdsso["password"])
login_button = driver.find_element_by_name("_eventId_proceed")
login_button.click() #Click login button

driver.implicitly_wait(10) # Wait up to 10 seconds to wait for elements to load on page

print(driver.current_url) #Print current page url

room_selection_link = driver.find_element_by_link_text("2019 Room Selection: Eligibility, Contract, Prepayment and Lottery Time & Checklist") #Begin navigation to vancancy webpage
room_selection_link.click()
print(driver.current_url)

room_selection_sixth = driver.find_element_by_xpath('//*[@rmscomponentid="11856"]')
print(room_selection_sixth)
room_selection_sixth.click()

vacancy_viewer = room_selection_sixth = driver.find_element_by_xpath('//*[@rmscomponentid="11831"]')
vacancy_viewer.click()

nav_button_next = driver.find_element_by_id('NavButtonNext')
nav_button_next.click()

driver.implicitly_wait(10) # Wait up to 10 seconds to wait for elements to load on page

apartments = driver.find_elements_by_xpath('//*[@rmssellevel="Building"]') #Finally at vacancy viewer, find all clickable building menus to display information for each
#print(apartments)
count_buildings = 0

apartment_information = pd.DataFrame(columns=['room_id', 'room_type', 'available_spaces', 'apt_building', 'floor', 'suite_id', 'bed_spaces', 'timestamp'])

while True:
        start_time = time.time()
        for building in apartments: #For each building we can click, click it and begin diving deeper and scraping its information
            if building != driver.find_element_by_id('ELAIDBuilding'):
                count_buildings+=1
                ##print("Number of Apartments", len(apartments)-1, "Count investigated", count_buildings)
                building.click()
                time.sleep(.05)
                driver.implicitly_wait(10) # Wait up to 10 seconds to wait for elements to load on page
                num_rows_opened = 0
                initial_rows_reported = len(driver.find_elements_by_xpath('//*//tr[@rmsrowmode="RoomRowCollapsed"]//td//img[@class="cbExpandRoomDetails"]'))
                ###print('initial recorded length: ', initial_rows_reported)
                while len(driver.find_elements_by_xpath('//*//tr[@rmsrowmode="RoomRowCollapsed"]//td//img[@class="cbExpandRoomDetails"]')) !=0:
                        ###print('room dropdowns to open: ',len(driver.find_elements_by_xpath('//*//tr[@rmsrowmode="RoomRowCollapsed"]//td//img[@class="cbExpandRoomDetails"]')))

                        try:
                                driver.implicitly_wait(0)
                                for room in driver.find_elements_by_xpath('//*//tr[@rmsrowmode="RoomRowCollapsed"]//td//img[@class="cbExpandRoomDetails"]'):
                                        room.click()
                                        num_rows_opened+=1
                        except NoSuchElementException: #Sometimes it tries to look for a room entry to expand despite there not being none left, pass is harmless
                                pass
                        except StaleElementReferenceException:
                                print('EXCEPTION ######################')
                                pass
                if initial_rows_reported > num_rows_opened:
                        print('Incomplete data! There is a row unopened that will bemissing from the table.')
                ###print('num rows opened: ',num_rows_opened)
                
                        
                        
                soup=BeautifulSoup(driver.page_source, 'lxml')
                timestamp = datetime.utcnow().timestamp()
                #print(soup)
                count=0
                suite_detail_information = soup.find_all('tr', class_="RoomSelectResultsSuiteRow")
                for suite in suite_detail_information:
                    suite_id = suite.find('a', class_="SuiteDetailInfo").span.string
                    ###print('suite_id', suite_id)
                    room_container = suite.find_next_sibling('tr')
                    #print(room_container)
                    rooms = room_container.find_all('tr', class_="RoomSelectResultsRoomRow")

                    for room in rooms:
                        room_availability = available_dissect(room.find_all('span')[1].string)
                        ##print('room_availability: ', room_availability)
                        room_id = room['rmsroomid']
                        ###print('room_id: ',room_id)
                        if room_availability == 0:
                                bed_space_container = room.find_next_siblings('tr')[1]
                        else:
                              bed_space_container = room.find_next_sibling('tr')   
                        bed_spaces = bed_space_container.find_all('tr',class_="bedSpaceContainerItem")
                        bed_space_list = []
                        #row_entry = make_array()
                        for bed_space in bed_spaces:
                            bed_space_id = bed_space['rmsbedspaceid']
                            ##print('bed_space_id: ',bed_space_id)
                            room_type = bed_space.find_all('span')[1].string
                            ###print('room_type: ',room_type)
                            bed_space_list.append(bed_space_id)
                        
                        row_entry = len(apartment_information)
                        apartment_information.loc[row_entry, 'room_id'] = room_id
                        apartment_information.loc[row_entry, 'room_type'] = room_type_dissect(room_type)
                        apartment_information.loc[row_entry, 'available_spaces'] = room_availability
                        apartment_information.loc[row_entry, 'apt_building'] = suite_name_dissect(suite_id)[1]
                        apartment_information.loc[row_entry, 'floor'] = suite_name_dissect(suite_id)[0]
                        apartment_information.loc[row_entry, 'suite_id'] = suite_id
                        apartment_information.loc[row_entry, 'bed_spaces'] = bed_space_list
                        apartment_information.loc[row_entry, 'timestamp'] = timestamp

        print(apartment_information.to_html())

        elapsed_time = time.time()-start_time
        print('elapsed_time', elapsed_time)
        #print(driver.current_url)
