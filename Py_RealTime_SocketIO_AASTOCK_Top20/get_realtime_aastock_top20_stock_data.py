import os
import time
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import msvcrt as m
import concurrent.futures
import re



symbol='Top20'
top20csvFileName = 'HK_Stock_Top20.csv'
EndDate = date.today() + timedelta(1)

dictWebDriver = {}


def buildWebDriver(symbol):

    if symbol in dictWebDriver:
        return dictWebDriver[symbol]

    #Initialize webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument(r"--user-data-dir=C:\Users\anthony\AppData\Local\Google\Chrome\User Data")
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=C:\Temp\ChromeProfile2')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')

    #disable images
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(executable_path="D:\chromedriver\chromedriver.exe", chrome_options=options)
    driver.delete_all_cookies()
    #set page load timeout = 20s
    driver.set_page_load_timeout(20)

    print('Start new driver for {0}: {1}'.format(symbol, driver.session_id))

    if symbol not in dictWebDriver:
        dictWebDriver[symbol] = driver

    return dictWebDriver[symbol]


def GetStockDatafromAAStock():
    print('Start getting Top20 data: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    retMsg = 'Download Data Success'
    try:

        driver = buildWebDriver(symbol)

        driver.get('http://www.aastocks.com/en/stocks/market/top-rank/stock?type=A&t=1&s=&o=1&p=')
        #driver.find_element_by_class_name('tab-sel').click()
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        soup = soup.find("table", {"id": "tbTS"})
        #print(soup)

        list = []
        new_table = pd.DataFrame(columns=range(0, 12), index = range(0, 21)) #Assume I know the size

        row_marker = 0
        for row in soup.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')        
            for column in columns:
                #if not column.text:
                #    continue
                m = re.findall('\d+.HK', column.text)
                #found=''
                if len(m) > 0:
                    found = m[0]            
                    #strText = re.sub('\d+.HK', '\n{0} '.format(found), column.text)
                    new_table.iat[row_marker, column_marker] = found
                else:
                    #new_table.iat[row_marker, column_marker] = column.text.strip()[0:6]
                    new_table.iat[row_marker, column_marker] = column.text.strip().replace('+','')
                column_marker += 1
            row_marker += 1


        df = pd.DataFrame()
        df=new_table.tail(20).copy()
        df.columns = ['Name/Symbol','SH-SZ/AH','Last','Chg','Chg %','Volume','Turnover','P/E','P/B','Yield','Market Cap','Chart']
        #df['DateTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df['DateTime'] = (datetime.now() + timedelta(hours=15)).strftime('%Y-%m-%d %H:%M:%S')

        #write the stock data for each ticker to csv
        for i in range(0, len(df)):
            ddf = df.iloc[[i]]
            #print(ddf)
            ticker = df.iloc[i]['Name/Symbol'][1:]
            #print(ticker)
            #ddf['Ticker'] = ticker[1:]
            with open('./data/{0}_{1}-{2}-{3}.csv'.format(ticker, EndDate.year, EndDate.month, EndDate.day), 'a') as f:
                ddf[['DateTime','Name/Symbol','Last','Chg','Chg %','Volume','Turnover','P/E','Market Cap']].to_csv(f, header=False, index=False, float_format='%.4f')

        #write the latest Top20 stock data to csv
        with open('./data/{0}'.format(top20csvFileName), 'w+') as f:
            df[['DateTime','Name/Symbol','Last','Chg','Chg %','Volume','Turnover','P/E','Market Cap']].to_csv(f, header=False, index=False, float_format='%.4f')

        print('End getting Top20 data: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    except Exception as e:
        print('Data Downloading Error: {0}'.format(str(e)))
        retMsg='Download Data Error: {0}'.format(str(e))

        try:
            driver.quit()
            print('Delete driver for {0}: {1}'.format(symbol, driver.session_id))
            del dictWebDriver[symbol]
        except KeyError as ex:
            print("No such key: '%s'" % ex.message)


        return retMsg


    return retMsg


if __name__ == '__main__':

    f_loc = './data/{0}'.format(top20csvFileName)
    #create the file if it does not exist
    if not os.path.exists(f_loc):
        open(f_loc, 'w').close()

    while(True):
        if m.kbhit():
            if m.getch() == b'q':
                break

        retMsg = ''

        try:
            #We can use a with statement to ensure threads are cleaned up promptly
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                # Start the load operations and mark each future with its URL
                future = executor.submit(GetStockDatafromAAStock)
                retMsg = future.result()

        except Exception as e:
            print('Restart Error: {0}'.format(str(e)))
            #driver.quit()
