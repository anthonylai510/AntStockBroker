#ThreadPoolExecutor Example
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import glob
import pandas as pd
import msvcrt as m
import concurrent.futures

import http.client
import socket
from selenium.webdriver.remote.command import Command


#Read ticker to DataFrame
filePath = './Ticker.csv'
df = pd.read_csv(filePath)


#Initialize webdriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument(r"--user-data-dir=C:\Users\anthony\AppData\Local\Google\Chrome\User Data")
options.add_argument('--profile-directory=Default')
options.add_argument('--user-data-dir=C:\Temp\ChromeProfile11')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--log-level=3')

#disable images
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

#options.binary_location = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
#driver = webdriver.Chrome(chrome_options=options)
#driver = webdriver.Chrome("D:\chromedriver\chromedriver.exe",chrome_options=options)
driver = webdriver.Chrome(executable_path="D:\chromedriver\chromedriver.exe", chrome_options=options)
driver.delete_all_cookies()
#set page load timeout > 30s
driver.set_page_load_timeout(20)

EndDate = date.today() + timedelta(1)


def get_status(driver):
    try:
        driver.execute(Command.STATUS)
        return 'Alive'
    except (socket.error, http.client.CannotSendRequest):
        return 'Dead'


#Function to get and save real-time stock data from Money18.com
def GetStockDatafromMoney18(symbol):
    returnMsg = 'Successfully getting and saving data for {0}'.format(symbol)
    print(symbol)
    symbol = symbol.replace('.HK', '')
    try:
        driver.get('http://money18.on.cc/eng/info/liveinfo_quote.html?symbol={0}'.format(symbol))
        html = driver.page_source
        #print(html)
        soup = BeautifulSoup(html, "lxml")
        #print(soup)
        soup = soup.find("div", {"id": "stock-info"})
        #print(soup)

        list = []
        soup1 = soup.find("div", {"id": "highlight"})
        soup1 = soup1.find_all("td")
        #print(soup1)
        #print('\n')
        for row in soup1:
            list.append(row.text)    

        soup2 = soup.find("div", {"id": "basic"})
        soup2 = soup2.find_all("td")
        #print(soup2)
        #print('\n')
        for row in soup2:
            list.append(row.text)

        #print(list)
        #print('\n')
        lName = list[::2]
        #print(lName)
        #print('\n')
        lValue = list[1::2]
        #print(lValue)
        #print('\n')

        dict = {}
        for i in range(len(lName)):
            dict[lName[i]] = lValue[i]  

        #print(dict)
        #print('\n')

        df = pd.DataFrame([dict])
        #df['DateTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df['DateTime'] = (datetime.now() + timedelta(hours=15)).strftime('%Y-%m-%d %H:%M:%S')
        df['Ticker'] = '{0}.HK'.format(symbol)
        df['Close'] = df['Price']

        df = df[['DateTime', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
        print(df)

        #open the file for append
        with open('./{0}.HK_{1}-{2}-{3}.csv'.format(symbol, EndDate.year, EndDate.month, EndDate.day), 'a') as f:
            df.to_csv(f, header=False, index=False)


    except Exception as e:
        returnMsg = 'Error getting and saving data for {0}: {1}'.format(symbol, str(e))
        print('Error getting and saving data for {0}: {1}'.format(symbol, str(e)))
        return returnMsg


    return returnMsg


#While loop to keep calling function to get and save real-time stock data
while(True):
    if m.kbhit():
        if m.getch() == b'q':
            break

    #We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # Start the load operations and mark each future with its URL
        #returnMsg = {executor.submit(GetStockDatafromMoney18, ticker): ticker for ticker in df['Ticker']}
        dictFuture = {executor.submit(GetStockDatafromMoney18, ticker): ticker for ticker in df['Ticker']}
        for future, value in dictFuture.items():
            #print(future.result())
            #print(value)

            retMsg = future.result()
            try:
                #print(retMsg)
                if 'Successfully' not in retMsg:
                    #close existing browser session
                    driverStatus = get_status(driver)
                    print('driver status: {0}'.format(driverStatus))
                    if 'Alive' in driverStatus:
                        print('Close existing driver session because of TimeoutException or Exception')
                        #driver.close()
                        driver.quit()
                        print('Close existing driver session done')

                    print('Start new driver session because of TimeoutException or Exception')
                    driver = webdriver.Chrome(executable_path="D:\chromedriver\chromedriver.exe", chrome_options=options)
                    driver.set_page_load_timeout(30)
                    print('New session id: {0}'.format(driver.session_id))
                    #GetStockDatafromMoney18(value)
            except Exception as e:
                print('Start new driver error: {0}'.format(str(e)))
                #driver = webdriver.Chrome(executable_path="D:\chromedriver\chromedriver.exe", chrome_options=options)
                #driver.set_page_load_timeout(30)


#driver.close()
driver.quit()