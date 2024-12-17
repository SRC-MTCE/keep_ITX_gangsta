###############################
#         GANG Watcher        #
#                             #
# CBC-RC - CAMEO-MTCE - by TG #
#            V 1.0            #
###############################

header = '''
    __ __                   _ __     ______                       __                     
   / //_/__  ___  ____     (_) /_   / ____/___ _____  ____ ______/ /_____ _   __  ______ 
  / ,< / _ \/ _ \/ __ \   / / __/  / / __/ __ `/ __ \/ __ `/ ___/ __/ __ `/  / / / / __ \\
 / /| /  __/  __/ /_/ /  / / /_   / /_/ / /_/ / / / / /_/ (__  ) /_/ /_/ /  / /_/ / /_/ /
/_/ |_\___/\___/ .___/  /_/\__/   \____/\__,_/_/ /_/\__, /____/\__/\__,_/   \__, /\____/ 
              /_/                                  /____/                  /____/        

    Log for ITX Ganging Watcher

    CBC-RC - CAMEO-MTCE - by TG

               V 1.0
__________________________________________________________________________________________

'''

from datetime import datetime, timedelta
from selenium import webdriver
import time
import win32com.client
from selenium.webdriver.common.by import By
import re
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
import sys
import psutil
import xml.etree.ElementTree as ET
import inspect
from selenium.webdriver.chrome.service import Service

itx_password = os.environ.get("itx_pwd")  
tag_password = os.environ.get("tag_pwd") 



###
#Creating Dictionnaries from XML
###


# Load the XML file
tree = ET.parse('lists.xml')
root = tree.getroot()

# Define the CHANNEL_URLS dictionary
CHANNEL_URLS = {}

# Generate the master_list
master_list = []
for channel in root.find('master_list').iter('channel'):
    master_list.append(channel.find('name').text)
    urls = [url.text for url in channel.findall('url')]
    CHANNEL_URLS[channel.find('name').text] = urls

# Generate the control_points list and COLOR_CP dictionary
control_points = []
COLOR_CP = {}
for control_point in root.find('control_points').iter('control_point'):
    control_points.append(control_point.find('name').text)
    COLOR_CP[control_point.find('name').text] = control_point.find('color').text


    

###
#Functions and Class
###

def terminate_chromedriver():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'chromedriver.exe' in proc.info['name']:
            log(f"Terminating chromedriver.exe with PID {proc.info['pid']}")
            proc.terminate()

#Channel Alarm Hashmap Class
class ChannelHashMap:
    def __init__(self, master_list, control_points):
        self.map = {}
        for channel in master_list:
            for control_point in control_points:
                key = f"{channel}"
                if key not in self.map:
                    self.map[key] = {}
                #That is not gracefull but puts everything back to Default state at start. Should be set to false when possible.
                self.map[key][control_point] = bool(False)

    def set_true(self, channel, control_point):
        if channel in self.map and control_point in self.map[channel]:
            self.map[channel][control_point] = bool(True)
        else:
            raise KeyError(f'Channel "{channel}" or control point "{control_point}" not found')

    def set_false(self, channel, control_point):
        if channel in self.map and control_point in self.map[channel]:
            self.map[channel][control_point] = bool(False)
        else:
            raise KeyError(f'Channel "{channel}" or control point "{control_point}" not found')

    def __str__(self):
        return str(self.map)

#Returns Hashmap API URLs by Channel     
def ch_function(ch):
    return CHANNEL_URLS.get(ch, [])

#Returns twins alarm state
def is_red(channel):
    return is_red_list[channel]

#GET TAG Tile config
def get_tag_api(url):
    username = "Admin"
    password = tag_password
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password))

    except:
        pass
    
    try:
        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            log(f"{url}GET request failed with status code:", response.status_code)
            return None
    except:
        pass

#PUT Tile color
def put_tag_api(json_data, color, is_txt=False, txt=None, is_url=False, url=None):
    if is_url:
        url_put = url
    
    elif is_txt:
        url_put = "http://10.169.8.106/api/5.0/layouts/config/8e9015f9-bd2f-4f03-b188-285bccb81899.json"
    else:
        url_put = "http://10.169.8.106/api/5.0/channels/config/16ac7c0f-0b66-4c84-8996-f73491a33d5d.json"
        
    username = "Admin"
    password = tag_password
    
    if is_txt:
        json_data["data"]["tiles"][5]["text_color"] = color
        json_data["data"]["tiles"][5]["text"] = txt
    else:
        json_data["data"]["profiles"][0]["border_color"] = color
        
    try:
        response_put = requests.put(url_put, auth=HTTPBasicAuth(username, password), json=json_data)
        put_response = response_put.status_code

        if put_response == 200:
            log("PUT attempt success")

        else:
            raise Exception (f"Response status code is {put_response}")
        
    except Exception as error:
        error_message=str(error)
        
        log(f"{error_message}")
        log(f"PUT Request failed on {url_put}. Terminate program with exit code 1")
        sys.exit(1)
            
    return put_response

#initialize chrome pages containing channels list
def init_chrome_drivers(channel):
    log(f"Opening Driver for Control Point {channel}")
    try:

        exe_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        chromedriver_path =  exe_dir + '/chromedriver_win64/chromedriver.exe' 
        print(chromedriver_path)
        # Initialize the Service with the chromedriver path
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument(f"google-chrome --app=http://fs-gvplatform.pres.cbcrc.ca/fstvmain/channel-ganging-webui/permission/{control_point}")
        driver = webdriver.Chrome(service=service, options=options)

        
        #driver = webdriver.Chrome()
        driver.get(f'http://fs-gvplatform.pres.cbcrc.ca/fstvmain/channel-ganging-webui/permission/{channel}')

        
        time.sleep(1)
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.Sendkeys("mtlitxadmin")
        time.sleep(0.1)
        shell.Sendkeys("{TAB}")
        time.sleep(0.1)
        shell.Sendkeys(itx_password)
        time.sleep(0.1)
        shell.Sendkeys("{ENTER}")
        time.sleep(4)
        driver.refresh()
        time.sleep(3)
        log(f"Success! Driver oppenned for Control Point {channel}")

    except Exception as error:
        error_message=str(error)
        print(error_message)
        log(error_message)
    return driver

#Returns list of the channels currently in the Control Point
def get_channel_list(driver):
    contents = []
    x = 1
    while True:
        try:
            elements = driver.find_elements(By.XPATH, f'//*[@id="gvApp"]/div[2]/div/div[2]/div[3]/ul/li[{x}]')
            if not elements:
                break
            content = elements[0].text
            contents.append(content)
            x += 1
        except Exception as error:
            error_message=str(error)
            print(error_message)
            log(error_message)
            log(f"Failed to retrieve shcedule on {driver}. Refreshing Driver")
            driver.refresh()
            #sys.exit(1)
            
    return tuple(contents)

#Logs useful info
def log(data_to_write):
    frame = inspect.currentframe().f_back
    line_number = frame.f_lineno
    function_name = frame.f_code.co_name

    if not os.path.isdir(".\\log"):
        os.makedirs(".\\log")
    filename_log = '.\\log\\'+ str(datetime.datetime.now().strftime('%Y-%m-%d')) + '-gang_alarm_tag.log'
    with open(filename_log, 'a') as logfile:
        logfile.write(str(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ': ' + f'Function {function_name}, Line {line_number}: {data_to_write}' + '\n')


def get_color(control_point):
    return COLOR_CP.get(control_point, "Orange")


#initializing
if __name__ == "__main__":
    terminate_chromedriver()
    print(header)
    log('''
__________________________________________

Starting...

Initializing Alarm List, Twin list and Chrome Drivers...
__________________________________________
''')
    channel_map = ChannelHashMap(master_list, control_points)
    is_red_list = {channel: False for channel in master_list}

# Initialize drivers outside the loop
drivers = {}
for control_point in control_points:
    drivers[control_point] = init_chrome_drivers(control_point)

log("Starting Schedule scanning")






url_list = ch_function("W18")

print(url_list)



# Main loop
while True:
    try:
        # Get channel lists inside the loop
        channel_lists = {}
        for control_point in control_points:
            channel_lists[control_point] = get_channel_list(drivers[control_point])

        for control_point in control_points:
            for channel in master_list:
                if channel in channel_lists[control_point] and channel_map.map[channel][control_point] == False:
                    color = get_color(control_point)



                    #NEW#
                    tag_api_url_ch_list = ch_function(channel)


                    for tag_api_url_ch in tag_api_url_ch_list :

                    
                        json_data_ch = get_tag_api(tag_api_url_ch)
                        
                        #PUT color according to Control Point
                        if json_data_ch:
                            log(f"Attempting PUT {color} on channel {channel}. Control Point: {control_point}")

                            put_response = put_tag_api(json_data_ch, color, is_url=True, url=tag_api_url_ch)

                            
                    channel_map.set_true(channel, control_point)
                    #NEW#





                        
                #Removing Channel from Control Point List
                elif channel not in channel_lists[control_point] and channel_map.map[channel][control_point] == True:
                    color="Default"


                    #NEW#
                    tag_api_url_ch_list = ch_function(channel)

                    for tag_api_url_ch in tag_api_url_ch_list:
                        
                        json_data_ch = get_tag_api(tag_api_url_ch)
                        
                        #PUT Default color according to Control Point
                        if json_data_ch:
                            log(f"Attempting PUT for Default. {channel} Removed from Gang: {control_point}")
                            put_response = put_tag_api(json_data_ch, color, is_url=True, url=tag_api_url_ch)
                            
                    channel_map.set_false(channel, control_point)
                    #NEW#


                    
                        
                            
                twin_drivers = control_points       
                #Check for Twin Channel in different Control Points.
                
                if sum(channel_map.map[channel][twin_driver] for twin_driver in twin_drivers) == 2:           
                    if not is_red(channel) :
                       
                        color="Yellow"

                        #NEW#
                        tag_api_url_ch_list = ch_function(channel)
                        for tag_api_url_ch in tag_api_url_ch_list:
                        
                            json_data_ch = get_tag_api(tag_api_url_ch)
                            log(f"Twins detected! {channel} is in one Control Point or more")
                            if json_data_ch:
                                put_response = put_tag_api(json_data_ch, color, is_url=True, url=tag_api_url_ch)
                                log(f"PUT {color} on channel {channel}.")

                        #NEW#
                            
                        is_red_list[channel] = True
                        
                #Removing Channel from Twin detection list.
                
                if sum(channel_map.map[channel][twin_driver] for twin_driver in twin_drivers) == 1  and is_red(channel)==True:
                    log(f"{channel} removed from Twins list. Setting alarms to False for {channel}")
                    is_red_list[channel] = False

                    for cp in control_points:
                        channel_map.set_false(channel, cp)
              
        time.sleep(0.5)

    except Exception as main_exception :
        log(f"Terminated! Main exception: {main_exception}")
        
    
