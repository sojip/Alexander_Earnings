from __future__ import absolute_import, unicode_literals
from copy_data import copydata
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
from datetime import datetime
import time
import random
import json
from application import celery_app

@celery_app.task(bind=True, name="task_search.search")
def search(self, start_date, end_date, earning, executable_path, firefox_binary):

    options = Options()
    options.headless = True
    
    #initialise driver
    driver = webdriver.Firefox(options = options, firefox_binary=firefox_binary, executable_path=executable_path )
    wait = WebDriverWait(driver, 30)
    driver.set_page_load_timeout(60)
    
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
    #first_month = " ".join(driver.find_element_by_xpath("//div[@id='Cal1']//h1").text.split())
    first_calendar = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='Cal1']//a[contains(@href,'calendar')]")))
    #first_calendar = driver.find_elements_by_xpath("//div[@id='Cal1']//a[contains(@href,'calendar')]")

    second_month = " ".join(wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='Cal2']//h1"))).text.split())
    #second_month = " ".join(driver.find_element_by_xpath("//div[@id='Cal2']//h1").text.split())
    second_calendar = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='Cal2']//a[contains(@href,'calendar')]")))
    #second_calendar = driver.find_elements_by_xpath("//div[@id='Cal2']//a[contains(@href,'calendar')]")

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
                #first_calendar = driver.find_elements_by_xpath("//div[@id='Cal1']//a[contains(@href,'calendar')]")
                if int(first_calendar[i].text) >= first_day and int(first_calendar[i].text) <= last_day:
                    
                    link = driver.find_element_by_xpath("//div[@id='Cal1']//a[contains(text(),{})]".format(first_calendar[i].text))
                    day = link.text
                    date = link.text + " " + first_month
                    link.click()
                    answer = copydata(driver, wait, earning, date)

                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': day, 'total': (last_day - first_day),
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)             
                        self.update_state(state='PROGRESS',
                            meta={'current': day, 'total': (last_day - first_day),
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
                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': day, 'total': (last_day - first_day),
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)
                    
                        self.update_state(state='PROGRESS',
                            meta={'current': day, 'total': (last_day - first_day),
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
                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': day, 'total':  int(first_calendar[-1].text) - first_day,
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)                 
                        self.update_state(state='PROGRESS',
                                meta={'current': day, 'total': int(first_calendar[-1].text) - first_day,
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
                    if json.loads(answer) != "OK":
                        self.update_state(state='FAILURE',
                            meta={'current': day, 'total':  int(first_calendar[-1].text),
                                    'message': "This error occured: {} while copying datas of {}".format(answer, date)})
                        return
                    else:
                        message = "Copyied datas for {}".format(date)
                        
                        self.update_state(state='PROGRESS',
                                meta={'current': day, 'total': int(second_calendar[-1].text),
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
    
    return {'current': "finished", 'total': len(earning['ticker']), 'message': 'Task completed!',
            'result': earnings_list}