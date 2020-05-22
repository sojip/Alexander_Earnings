from __future__ import absolute_import, unicode_literals
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys #to actually send keys to webpage as if we were on keyboard
from selenium.webdriver.support.ui import WebDriverWait #to wait
from selenium.webdriver.support import expected_conditions as EC #to define conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import MaxRetryError
from selenium import webdriver #for browser sessions
import time
import random
from application import celery_app

@celery_app.task(bind=True, name="task_crossreference.crossreference")
def crossreference(self, earning, executable_path, firefox_binary):
    options = Options()
    options.headless = True
    
    print(earning)
    
    #initilalise driver
    driver = webdriver.Firefox(executable_path=executable_path, firefox_binary=firefox_binary, options = options)
    wait = WebDriverWait(driver, 30)
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
            #update state
            self.update_state(state='FAILURE',
                            meta={'current': earning['ticker'].index(ticker), 'total': len(earning['ticker']),
                                    'message': "Error selecting option chain for {}".format(ticker)})
            driver.quit()
            return
        
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
        
        self.update_state(state='PROGRESS',
                            meta={'current': earning['ticker'].index(ticker), 'total': len(earning['ticker']),
                                    'message': "copyied datas for {}".format(ticker)})
        
        time.sleep(random.randrange(5,11))
    
    # Create an empty list 
    cboe_list = [] 
    
    for i in range (len(data['Tickers'])):
        cboe_list.append([data['Tickers'][i], data['Stock_Price'][i],data['Call_Last'][i],
                          data['Call_Ask'][i], data['Call_Int'][i], data['Call_Volume'][i], 
                          data['Put_Last'][i], data['Put_Ask'][i], data['Put_Int'][i], 
                          data['Put_Volume'][i]])
        
    driver.quit()
  
    return {'current': "finished", 'total': len(earning['ticker']), 'message': 'Task completed!',
            'result': cboe_list}