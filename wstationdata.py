#Automatic Weather Station
import json
import sys
import time
import datetime
import gspread
import psutil
import subprocess
from system_info import get_temperature
from oauth2client.service_account import ServiceAccountCredentials
from sense_hat import SenseHat
GDOCS_OAUTH_JSON       = 'rbpidata-260116-fd3571ba1190.json'
GDOCS_SPREADSHEET_NAME = 'wstationdata'
FREQUENCY_SECONDS      = 10
def login_open_sheet(oauth_key_file, spreadsheet):
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, 
                      scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive'])
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet. Check OAuth credentials, spreadsheet name, and')
        print('make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)

sense = SenseHat()
sense.clear()
print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)


    temp     = sense.get_temperature()
    temp     = round(temp, 1)
    humidity = sense.get_humidity()
    humidity = round(humidity, 1)
    pressure = sense.get_pressure()
    pressure = round(pressure, 1)

    sense.clear()
    sense.show_message(" T:" + str(temp) + "C " + " H:" + str(humidity) + "% " + " P:" + str(pressure) + "hpa", scroll_speed=(0.10), back_colour= [0,0,200]) 
 
    print ("Temperature C:",temp)
    print ("Humidity:",humidity)
    print ("pressure:",pressure)



    try:
        worksheet.append_row((datetime.datetime.now(), temp,humidity,pressure))
#        worksheet.append_row((dat, cpu, tmp))
# gspread==0.6.2
# https://github.com/burnash/gspread/issues/511  
    except:
        print('Append error, logging in again')
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue
    print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    time.sleep(FREQUENCY_SECONDS)
