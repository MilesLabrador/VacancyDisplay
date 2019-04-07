from   selenium import webdriver
from   selenium.common.exceptions import TimeoutException
from AUTH import ucsdsso
import time
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
for building in apartments: #For each building we can click, click it and begin diving deeper and scraping its information
    if building != driver.find_element_by_id('ELAIDBuilding'):
        count_buildings+=1
        #print("Number of Apartments", len(apartments)-1, "Count investigated", count_buildings)
        building.click()
        time.sleep(.05)
        
        rooms = driver.find_elements_by_class_name('cbExpandRoomDetails') #Find each room element we must click to display room information
        count_room = 0
        for room in rooms:
            count_room+=1
            #print(len(rooms), 'Rooms expanded: ',count_room)
            time.sleep(.10)
            room.click()

        suite_information = driver.find_elements_by_xpath('//div[@id="RoomRowsScrollableContainer"]//table//tbody//*//tbody//tr') #
        for item in suite_information:
            if item.get_attribute('class') == 'RoomSelectResultsSuiteRow':
                suite_id = item.find_element_by_xpath('//a[@class = "SuiteDetailInfo"]//span').text
                #print('suite_id', suite_id)
            else:
                n=0
                room_id_elements = item.find_elements_by_xpath('//tr[@class="RoomSelectResultsRoomRow"]')
                for room_id_element in room_id_elements:
                    room_id = room_id_element.get_attribute('rmsroomid')
                    #print('room_id', room_id)
                    available = item.find_elements_by_xpath('//tr[@rmsroomid="'+room_id+'"]//span')[1].text
                    #print("ROOM AVAILABILITY",available)
                    
                    bed_space_elements = item.find_elements_by_xpath('//table[@rmsroomid="'+room_id+'"]//tr[@class="bedSpaceContainerItem"]')
                    for bed_space_element in bed_space_elements:
                        bed_space_id = bed_space_element.get_attribute('rmsbedspaceid')
                        #print('bed space id', bed_space_id)
                        room_type = bed_space_element.find_elements_by_xpath('.//td//span')[1].text
                        #print('room type', room_type)
            print('suite')
                    


print(driver.current_url)

