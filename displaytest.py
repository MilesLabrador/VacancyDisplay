from   selenium import webdriver
from   selenium.common.exceptions import TimeoutException
from AUTH import ucsdsso
import time
from bs4 import BeautifulSoup
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
start_time = time.time()
for building in apartments: #For each building we can click, click it and begin diving deeper and scraping its information
    if building != driver.find_element_by_id('ELAIDBuilding'):
        count_buildings+=1
        print("Number of Apartments", len(apartments)-1, "Count investigated", count_buildings)
        building.click()
        time.sleep(.05)
        
        rooms = driver.find_elements_by_class_name('cbExpandRoomDetails') #Find each room element we must click to display room information
        count_room = 0
        for room in rooms:
            count_room+=1
            print(len(rooms), 'Rooms expanded: ',count_room)
            time.sleep(.1)
            room.click()

        soup=BeautifulSoup(driver.page_source, 'lxml')
        #print(soup)
        count=0
        suite_detail_information = soup.find_all('tr', class_="RoomSelectResultsSuiteRow")
        for suite in suite_detail_information:
            suite_id = suite.find('a', class_="SuiteDetailInfo").span.string
            print('suite_id', suite_id)
            room_container = suite.find_next_sibling('tr')
            #print(room_container)
            rooms = room_container.find_all('tr', class_="RoomSelectResultsRoomRow")
            for room in rooms:
                room_availability = room.find_all('span')[1].string
                print('room_availability: ', room_availability)
                room_id = room['rmsroomid']
                print('room_id: ',room_id)
                bed_space_container = room.find_next_sibling('tr')
                bed_spaces = bed_space_container.find_all('tr',class_="bedSpaceContainerItem")
                for bed_space in bed_spaces:
                    bed_space_id = bed_space['rmsbedspaceid']
                    print('bed_space_id: ',bed_space_id)
                    room_type = bed_space.find_all('span')[1].string
                    print('room_type: ',room_type)

elapsed_time = time.time()-start_time
print(elapsed_time)
print(driver.current_url)

