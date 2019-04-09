from   selenium import webdriver
from   selenium.common.exceptions import TimeoutException
from AUTH import ucsdsso
import time
from bs4 import BeautifulSoup
from datascience import *
import numpy as np

def available_dissect(room_availability):
        return int(room_availability.replace('(', '').replace(')','').replace('available',''))
def room_type_dissect(room_type):
    if 'single' in room_type.lower():
        return 'single'
    elif 'double' in room_type.lower():
        return 'double'
    elif 'triple' in room_type.lower():
        return 'triple'
def suite_name_dissect(suite_id):
    parts = suite_id.split('-')
    #print(suite_id)
    if 'MTH' in parts[0].upper():
        floor = None
        apartment_building = parts[0]+'-'+'00'
    else:
        floor = parts[1][3]
        apartment_building = parts[0]+'-'+parts[1][0:2]+'00'
    return (floor, apartment_building)


driver = webdriver.Firefox()

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


while True:
        start_time = time.time()
        apartment_information = Table(make_array('room_id', 'room_type', 'available_spaces', 'apt_building', 'floor', 'suite_id', 'bed_spaces'))
        for building in apartments: #For each building we can click, click it and begin diving deeper and scraping its information
            if building != driver.find_element_by_id('ELAIDBuilding'):
                count_buildings+=1
                ##print("Number of Apartments", len(apartments)-1, "Count investigated", count_buildings)
                building.click()
                time.sleep(.05)
                
                rooms = driver.find_elements_by_xpath('//*//img[@class="cbExpandRoomDetails"]') #Find each room element we must click to display room information
                count_room = 0
                for room in rooms:
                    count_room+=1
                    ##print(len(rooms), 'Rooms expanded: ',count_room)
                    time.sleep(.01)
                    room.click()
                time.sleep(.7)
                soup=BeautifulSoup(driver.page_source, 'lxml')
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
                        bed_space_array = make_array()
                        row_entry = make_array()
                        for bed_space in bed_spaces:
                            bed_space_id = bed_space['rmsbedspaceid']
                            ##print('bed_space_id: ',bed_space_id)
                            room_type = bed_space.find_all('span')[1].string
                            ###print('room_type: ',room_type)
                            bed_space_array = np.append(bed_space_array, bed_space_id)

                        row_entry = np.append(row_entry, room_id)#
                        row_entry = np.append(row_entry, room_type_dissect(room_type))#
                        row_entry = np.append(row_entry, room_availability)#
                        row_entry = np.append(row_entry, suite_name_dissect(suite_id)[1])#
                        row_entry = np.append(row_entry, suite_name_dissect(suite_id)[0])#
                        row_entry = np.append(row_entry, suite_id)#
                        row_entry = np.append(row_entry, make_array(bed_space_array))#
                        ###print("LEN: ",len(row_entry), row_entry)
                        apartment_information = apartment_information.with_rows(make_array(row_entry))

        elapsed_time = time.time()-start_time
        print('elapsed_time', elapsed_time)
        print(driver.current_url)

