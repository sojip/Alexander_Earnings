from __future__ import absolute_import, unicode_literals
from copy_data import copydata
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys #to actually send keys to webpage as if we were on keyboard
from selenium.webdriver.support.ui import WebDriverWait #to wait
from selenium.webdriver.support import expected_conditions as EC #to define conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import MaxRetryError
from selenium import webdriver #for browser sessions
from datetime import datetime
import time
import random
import json
from application import celery_app
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@celery_app.task(bind=True, name="tasks.search")
def search(self, start_date, end_date, earning):

    options = Options()
    options.headless = True
    
    #initialise driver
    driver = webdriver.Remote(command_executor='http://172.18.0.2:4444/wd/hub', desired_capabilities=DesiredCapabilities.FIREFOX, options = options)
    wait = WebDriverWait(driver, 90)
    driver.set_page_load_timeout(90)
    
    site = "https://earningwhispers.com" 
    
    try:
        # go to the earningwhisper website
        driver.get("https://earningswhispers.com/calendar")
    except TimeoutException:
        #update state
        self.update_state(state='FAILURE',
                            meta={'current': 0, 'total': 0,
                                    'message': "Time Out Error"})
        driver.quit()
        return
    
    except MaxRetryError:
        #update state
        self.update_state(state='FAILURE',
                            meta={'current': 0, 'total': 0,
                                    'message': "Max Retry Error"})
        driver.quit() 
        return
    except:
        #update state
        self.update_state(state='FAILURE',
                            meta={'current': 0, 'total': 0,
                                    'message': "An Error Occured Opening {}".format(site)})
        driver.quit()
        return


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
    first_month = " ".join(wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='Cal1']//h1"))).text.split())
    try:
        first_calendar = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='Cal1']//a[contains(@href,'calendar')]")))
    except TimeoutException:
        pass
        
    second_month = " ".join(wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='Cal2']//h1"))).text.split())
    second_calendar = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='Cal2']//a[contains(@href,'calendar')]")))

    if start_date.split('-')[1] == end_date.split('-')[1]:
        # transform dates string into date objects
        start_date = start_date[2:]
        date_object = datetime.strptime(start_date, '%y-%m-%d')
        date_ = date_object.strftime("%B %d %Y")
        s = date_.split()[0] + " " + date_.split()[2]
        date = " ".join(s.split())

        if date == first_month:
            for i in range (len(first_calendar)):
                first_calendar = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='Cal1']//a[contains(@href,'calendar')]")))
                if int(first_calendar[i].text) >= first_day and int(first_calendar[i].text) <= last_day:
                    
                    link = driver.find_element_by_xpath("//div[@id='Cal1']//a[contains(text(),{})]".format(first_calendar[i].text))
                    day = link.text
                    date = link.text + " " + first_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    
                    current = int(day) - first_day + 1
                    total = last_day - first_day + 1

                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': current, 'total': total,
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)             
                        self.update_state(state='PROGRESS',
                            meta={'current': current, 'total': total,
                                    'message': message})
                else:
                    continue
                    
                time.sleep(random.randrange(1,10))

        elif date == second_month:
            for i in range (len(second_calendar)):
                second_calendar = driver.find_elements_by_xpath("//div[@id='Cal2']//a[contains(@href,'calendar')]")
                if int(second_calendar[i].text) >= first_day and int(second_calendar[i].text) <= last_day:
                    link = driver.find_element_by_xpath("//div[@id='Cal2']//a[contains(text(),{})]".format(second_calendar[i].text))
                    day = link.text
                    date = link.text + " " + second_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    
                    current = int(day) - first_day + 1
                    total = last_day - first_day + 1
                    
                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': current, 'total': total,
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)
                    
                        self.update_state(state='PROGRESS',
                            meta={'current': current, 'total': total,
                                    'message': message})
                    
                time.sleep(random.randrange(1,10))

        else:
            self.update_state(state='FAILURE',
                            meta={'current': 0, 'total': 0,
                                    'message': "Bad Values of dates"})        
            driver.quit()
            
            return

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
                    day = link.text
                    date = link.text + " " + first_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    
                    current = int(day) - first_day + 1
                    total = int(first_calendar[-1].text) - first_day + 1
                    
                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': current, 'total':  total,
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)                 
                        self.update_state(state='PROGRESS',
                                meta={'current': current, 'total': total,
                                        'message': message})

                
                time.sleep(random.randrange(1,10))
            
            for i in range (len(second_calendar)):
                second_calendar = driver.find_elements_by_xpath("//div[@id='Cal2']//a[contains(@href,'calendar')]")
                if int(second_calendar[i].text) <= last_day:
                    link = driver.find_element_by_xpath("//div[@id='Cal2']//a[contains(text(),{})]".format(second_calendar[i].text))
                    day = link.text
                    date = link.text + " " + second_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)
                    
                    current = int(day) - 1 + 1
                    total = int(second_calendar[-1].text) + 1
                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': current, 'total':  total,
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)
                        
                        self.update_state(state='PROGRESS',
                                meta={'current': current, 'total': total,
                                        'message': message})

                time.sleep(random.randrange(1,10))
        else:
            self.update_state(state='FAILURE',
                meta={'current': 0, 'total': 0,
                        'message': "Bad Values of Dates"})
            driver.quit()
            return
    
    # Create an empty list 
    earnings_list =[] 
    
    for i in range (len(earning['ticker'])):
        earnings_list.append([earning['ticker'][i], earning['date'][i], earning['time'][i]])
        
    driver.quit()
    
    return {'current': 100, 'total': 100, 'message': 'Task completed!',
            'result': earnings_list}
    




@celery_app.task(bind=True, name="tasks.crossreference")
def crossreference(self, tickers_list):
    options = Options()
    options.headless = True
    
    #initilalise driver
    driver = webdriver.Remote(command_executor='http://172.18.0.2:4444/wd/hub', desired_capabilities=DesiredCapabilities.FIREFOX, options = options)
    wait = WebDriverWait(driver, 60)
    driver.set_page_load_timeout(60)
    
    site = "https://www.cboe.com"
    
    #open cboe website
    try:
        driver.get("http://www.cboe.com/delayedquote/quotes-dashboard")
    except:
         #update state
        self.update_state(state='FAILURE',
                            meta={'current': 0, 'total': 0,
                                    'message': "An Error Occured Opening {}".format(site)})
        driver.quit()
        return

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
    
    print(tickers_list)

    #lookup each ticker
    for i in range (len(tickers_list)):
        try:
            query =  wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='symbol']")))                      
            query.clear()
            query.send_keys(tickers_list[i])
            button = driver.find_element_by_xpath("//div[@class='search-component']//button[@type='submit']")
            overlay = driver.find_element_by_class_name("cookie-msg-cntr")
            driver.execute_script("arguments[0].style.visibility='hidden'", overlay)
            button.click()
        except:
            #update state
            self.update_state(state='FAILURE',
                                meta={'current': 0, 'total': 0,
                                        'message': "Error selecting search"})
            driver.quit()
            return
        
        try:
            options_chains = wait.until(EC.presence_of_element_located((By.ID, "ancOpCH")))
            overlay = driver.find_element_by_class_name("cookie-msg-cntr")
            driver.execute_script("arguments[0].style.visibility='hidden'", overlay)
            options_chains.click()
        except ElementNotInteractableException:
            
            data['Tickers'].append(tickers_list[i])
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
            #update state
            self.update_state(state='FAILURE',
                            meta={'current': i, 'total': len(tickers_list),
                                    'message': "Error selecting option chain for {}".format(tickers_list[i])})
            driver.quit()
            return
        
        stock_price = wait.until(EC.presence_of_element_located((By.ID, "summary-last"))).text
        
        #calls table rows
        calls = driver.find_elements_by_xpath("//table[@id='tblCalls']//tbody//tr")
        #put table rows
        puts = driver.find_elements_by_xpath("//table[@id='tblPuts']//tbody//tr")
        
        strikes = driver.find_elements_by_xpath("//table[@id='tblStrike']//tbody//td")
        for j in range (len(strikes)):
            try:
                if float(strikes[j].text.split()[1]) <= float(stock_price) and float(strikes[j+1].text.split()[1]) >= float(stock_price):
                    calls_row = calls[j].text
                    puts_row = puts[j+1].text
                    
                    call_last = calls_row.split()[0]
                    call_ask = calls_row.split()[3]
                    call_vol = calls_row.split()[4]
                    call_int = calls_row.split()[8]
                    put_last = puts_row.split()[0]
                    put_ask = puts_row.split()[3]
                    put_vol = puts_row.split()[4]
                    put_int = puts_row.split()[8]
                    
                    data['Tickers'].append(tickers_list[i])
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
            except:
                continue
        if tickers_list[i] not in data['Tickers']:
            data['Tickers'].append(tickers_list[i])
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
        
        self.update_state(state='PROGRESS',
                            meta={'current': i, 'total': len(tickers_list),
                                    'message': "copyied datas for {}".format(tickers_list[i])})
        
        time.sleep(random.randrange(5,11))
    
    # Create an empty list 
    cboe_list = [] 
    
    for i in range (len(data['Tickers'])):
        cboe_list.append([data['Tickers'][i], data['Stock_Price'][i],data['Call_Last'][i],
                          data['Call_Ask'][i], data['Call_Int'][i], data['Call_Volume'][i], 
                          data['Put_Last'][i], data['Put_Ask'][i], data['Put_Int'][i], 
                          data['Put_Volume'][i]])
        
    driver.quit()
  
    return {'current': 100, 'total': 100, 'message': 'Task completed!',
            'result': cboe_list}