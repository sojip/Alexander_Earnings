from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from selenium import webdriver #for browser sessions
from selenium.webdriver.common.keys import Keys #to actually send keys to webpage as if we were on keyboard
from selenium.webdriver.support.ui import WebDriverWait #to wait
from selenium.webdriver.support import expected_conditions as EC #to define conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import MaxRetryError
from copy_data import copydata
from datetime import datetime
import time
import random
import pandas as pd
import json


app = Flask(__name__)



#initialise webdriver options
options = Options()
options.headless = True


#global variables
earning = {}
earning['ticker'] = []
earning['date'] = []
earning['time']= []




@app.route('/')
def acceuil():
    return render_template('acceuil.html')

@app.route('/search', methods=['POST'])
def search():
    #initialise driver
    driver = webdriver.Firefox(options = options)
    wait = WebDriverWait(driver, 30)
    driver.set_page_load_timeout(60)
    
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    try:
        # go to the earningwhisper website
        driver.get("https://earningswhispers.com/calendar")
    except TimeoutException:
        # send alert to ask user to wait
        driver.quit()
        return jsonify("Time Out")
    except MaxRetryError:
        driver.quit() 
        return jsonify("Max Retry")
    except:
        driver.quit()
        return jsonify("Error opening site")


    # select list view option
    lv_option = wait.until(EC.presence_of_element_located((By.ID, "lv")))
    driver.execute_script("arguments[0].setAttribute('style','display:inline;')",lv_option)
    lv_coordinates = lv_option.location
    driver.execute_script("window.scrollTo(0, arguments[0])", lv_coordinates.get('y'))
    lv_overlay = driver.find_element_by_tag_name("header")
    driver.execute_script("arguments[0].style.visibility='hidden'", lv_overlay)
    lv_option.click()

    # days for earnings
    first_day = int(start_date.split('-')[2])
    last_day = int(end_date.split('-')[2])


    # calendars
    first_month = " ".join(driver.find_element_by_xpath("//div[@id='Cal1']//h1").text.split())
    first_calendar = driver.find_elements_by_xpath("//div[@id='Cal1']//a[contains(@href,'calendar')]")

    second_month = " ".join(driver.find_element_by_xpath("//div[@id='Cal2']//h1").text.split())
    second_calendar = driver.find_elements_by_xpath("//div[@id='Cal2']//a[contains(@href,'calendar')]")

    if start_date.split('-')[1] == end_date.split('-')[1]:
        # transform dates string into date objects
        start_date = start_date[2:]
        date_object = datetime.strptime(start_date, '%y-%m-%d')
        date_ = date_object.strftime("%B %d %Y")
        s = date_.split()[0] + " " + date_.split()[2]
        date = " ".join(s.split())

        if date == first_month:
            for i in range (len(first_calendar)):
                first_calendar = driver.find_elements_by_xpath("//div[@id='Cal1']//a[contains(@href,'calendar')]")
                if int(first_calendar[i].text) >= first_day and int(first_calendar[i].text) <= last_day:
                    link = driver.find_element_by_xpath("//div[@id='Cal1']//a[contains(text(),{})]".format(first_calendar[i].text))
                    date = link.text + " " + first_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    if json.loads(answer) != "OK":
                        return (answer)
                    
                time.sleep(random.randrange(1,10))

        elif date == second_month:
            for i in range (len(second_calendar)):
                second_calendar = driver.find_elements_by_xpath("//div[@id='Cal2']//a[contains(@href,'calendar')]")
                if int(second_calendar[i].text) >= first_day and int(second_calendar[i].text) <= last_day:
                    link = driver.find_element_by_xpath("//div[@id='Cal2']//a[contains(text(),{})]".format(second_calendar[i].text))
                    date = link.text + " " + second_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    if json.loads(answer) != "OK":
                        return (answer)
                time.sleep(random.randrange(1,10))
        else:
            driver.quit()
            return jsonify("Bad Value Of Dates")

    else:
        start_date = start_date[2:]
        date_object_1 = datetime.strptime(start_date, '%y-%m-%d')
        date_1_ = date_object_1.strftime("%B %d %Y")
        s_1 = date_1_.split()[0] + " " + date_1_.split()[2]
        date_1 = " ".join(s_1.split())

        end_date = end_date[2:]
        date_object_2 = datetime.strptime(end_date, '%y-%m-%d')
        date_2_ = date_object_2.strftime("%B %d %Y")
        s_2 = date_2_.split()[0] + " " + date_2_.split()[2]
        date_2 = " ".join(s_2.split())
    
        if date_1 == first_month and date_2 == second_month:
            for i in range (len(first_calendar)):
                first_calendar = driver.find_elements_by_xpath("//div[@id='Cal1']//a[contains(@href,'calendar')]")
                if int(first_calendar[i].text) >= first_day and int(first_calendar[i].text) <= int(first_calendar[-1].text):
                    link = driver.find_element_by_xpath("//div[@id='Cal1']//a[contains(text(),{})]".format(first_calendar[i].text))
                    date = link.text + " " + first_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    if json.loads(answer) != "OK":
                        return (answer)
                time.sleep(random.randrange(1,10))
            
            for i in range (len(second_calendar)):
                second_calendar = driver.find_elements_by_xpath("//div[@id='Cal2']//a[contains(@href,'calendar')]")
                if int(second_calendar[i].text) <= last_day:
                    link = driver.find_element_by_xpath("//div[@id='Cal2']//a[contains(text(),{})]".format(second_calendar[i].text))
                    date = link.text + " " + second_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    if json.loads(answer) != "OK":
                        return (answer)
                time.sleep(random.randrange(1,10))
        else:
            driver.quit()
            return("Bad Value Of Dates")

    # #store in excel file
    # df = pd.DataFrame(earning)
    
    # Create an empty list 
    earnings_list =[] 
    
    # # Iterate over each row 
    # for index, rows in df.iterrows(): 
    #     # Create list for the current row 
    #     my_list =[rows.ticker, rows.date, rows.time] 
        
    #     # append the list to the final list 
    #     earnings_list.append(my_list)
    
    for i in range (len(earning['ticker'])):
        earnings_list.append([earning['ticker'][i], earning['date'][i], earning['time'][i]])
        
    driver.quit()
  
    return jsonify(earnings_list)

@app.route('/crossreference', methods=['GET'])
def get_datas():
    #initilalise driver
    driver = webdriver.Firefox(options = options)
    wait = WebDriverWait(driver, 90)
    #open cboe website
    try:
        driver.get("http://www.cboe.com/delayedquote/quotes-dashboard")
    except:
        driver.quit()
        return("Error opening site")

    data = {}
    data['Tickers'] = []
    data['Stock_Price'] = []
    data['Call_Last'] = []
    data['Call_Ask'] = []
    data['Call_Int'] = []
    data['Call_Volume'] = []
    data['Put_Last'] = []
    data['Put_Ask'] = []
    data['Put_Int'] = []
    data['Put_Volume'] = []

    #lookup each ticker
    for ticker in earning['ticker']:
        try:
            query =  wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='symbol']")))                      
            query.clear()
            query.send_keys(ticker)
            button = driver.find_element_by_xpath("//div[@class='search-component']//button[@type='submit']")
            overlay = driver.find_element_by_class_name("cookie-msg-cntr")
            driver.execute_script("arguments[0].style.visibility='hidden'", overlay)
            button.click()
        except:
            driver.quit()
            return jsonify("Error selecting search")
        
        try:
            options_chains = wait.until(EC.presence_of_element_located((By.ID, "ancOpCH")))
            overlay = driver.find_element_by_class_name("cookie-msg-cntr")
            driver.execute_script("arguments[0].style.visibility='hidden'", overlay)
            options_chains.click()
        except ElementNotInteractableException:
            
            data['Tickers'].append(ticker)
            data['Stock_Price'].append("No Value")
            data['Call_Last'].append("No Value")
            data['Call_Ask'].append("No Value")
            data['Call_Int'].append("No Value")
            data['Call_Volume'].append("No Value")
            data['Put_Last'].append("No Value")
            data['Put_Ask'].append("No Value")
            data['Put_Int'].append("No Value")
            data['Put_Volume'].append("No Value")
                    
            driver.back()
            continue
        except:
            driver.quit()
            return jsonify("Error selecting option chain")
        
        stock_price = wait.until(EC.presence_of_element_located((By.ID, "summary-last"))).text
        
        #calls table rows
        calls = driver.find_elements_by_xpath("//table[@id='tblCalls']//tbody//tr")
        #put table rows
        puts = driver.find_elements_by_xpath("//table[@id='tblPuts']//tbody//tr")
        
        strikes = driver.find_elements_by_xpath("//table[@id='tblStrike']//tbody//td")
        for i in range (len(strikes)):
            if float(strikes[i].text.split()[1]) <= float(stock_price) and float(strikes[i+1].text.split()[1]) >= float(stock_price):
                calls_row = calls[i].text
                puts_row = puts[i+1].text
                
                call_last = calls_row.split()[0]
                call_ask = calls_row.split()[3]
                call_vol = calls_row.split()[4]
                call_int = calls_row.split()[8]
                put_last = puts_row.split()[0]
                put_ask = puts_row.split()[3]
                put_vol = puts_row.split()[4]
                put_int = puts_row.split()[8]
                
                data['Tickers'].append(ticker)
                data['Stock_Price'].append(stock_price)
                data['Call_Last'].append(call_last)
                data['Call_Ask'].append(call_ask)
                data['Call_Int'].append(call_int)
                data['Call_Volume'].append(call_vol)
                data['Put_Last'].append(put_last)
                data['Put_Ask'].append(put_ask)
                data['Put_Int'].append(put_int)
                data['Put_Volume'].append(put_vol)
                break
            else:
                continue
        if ticker not in data['Tickers']:
            data['Tickers'].append(ticker)
            data['Stock_Price'].append("No Value")
            data['Call_Last'].append("No Value")
            data['Call_Ask'].append("No Value")
            data['Call_Int'].append("No Value")
            data['Call_Volume'].append("No Value")
            data['Put_Last'].append("No Value")
            data['Put_Ask'].append("No Value")
            data['Put_Int'].append("No Value")
            data['Put_Volume'].append("No Value")
            
        driver.back()
        driver.back()
        
        time.sleep(random.randrange(5,11))
    
    # frame = pd.DataFrame(data)
    
    # Create an empty list 
    cboe_list = [] 
    
    # # Iterate over each row 
    # for index, rows in frame.iterrows(): 
    #     # Create list for the current row 
    #     my_list =[rows.Tickers, rows.Stock_Price, rows.Call_Last,
    #               rows.Call_Ask, rows.Call_Int, rows.Call_Volume, 
    #               rows.Put_Last, rows.Put_Ask, rows.Put_Int, 
    #               rows.Put_Volume ]
        
    #     # append the list to the final list 
    #     cboe_list.append(my_list)
    
    for i in range (len(data['Tickers'])):
        cboe_list.append([data['Tickers'][i], data['Stock_Price'][i],data['Call_Last'][i],
                          data['Call_Ask'][i], data['Call_Int'][i], data['Call_Volume'], 
                          data['Put_Last'][i], data['Put_Ask'][i], data['Put_Int'][i], 
                          data['Put_Volume'][i]])
        
    driver.quit()
  
    return jsonify(cboe_list)