
from selenium.webdriver.support import expected_conditions as EC #to define conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json


#function to copy data after selecting a date
def copydata(driver, wait, earning, date):
    try:
        #select all option
        all_option = wait.until(EC.presence_of_element_located((By.ID, "All")))
        driver.execute_script("arguments[0].setAttribute('style','display:inline;')",all_option)
        all_coordinates = all_option.location
        driver.execute_script("window.scrollTo(0, arguments[0])", all_coordinates.get('y'))
        all_overlay = driver.find_element_by_tag_name('header')
        driver.execute_script("arguments[0].style.visibility='hidden'", all_overlay)
        all_option.click()
    except:
        driver.quit()
        return json.dumps("Error selecting all")

    
    try:
        #click on show more button
        show_more_button = driver.find_element_by_id("showmore")
        show_more_button.click()
        element = wait.until(EC.presence_of_element_located((By.ID, "morecalendar")))
        del element
    
    except NoSuchElementException:
        #copy data
        tickers = driver.find_elements_by_class_name('ticker')
        time_title = driver.find_element_by_id("time")
        actual_title = driver.find_element_by_id("actual")
        if time_title.is_displayed():
            for i in range (len(tickers)):       
                time = driver.find_elements_by_class_name('time')
                tickers_ = driver.find_elements_by_class_name('ticker')
                if tickers_[i].text != '':
                    earning['ticker'].append(tickers_[i].text)
                    earning['date'].append(date)
                    earning['time'].append(time[i].text)
        elif actual_title.is_displayed():
            for i in range (len(tickers)):
                time = driver.find_elements_by_class_name('time')
                actual = driver.find_elements_by_css_selector("div[class^='actual']")
                tickers_ = driver.find_elements_by_class_name('ticker')
                if i < len(actual):
                    if tickers_[i].text != '':
                        earning['ticker'].append(tickers_[i].text)
                        earning['date'].append(date)
                        earning['time'].append(actual[i].text)
                elif i >= len(actual):
                    if tickers_[i].text != '':
                        earning['ticker'].append(tickers_[i].text)
                        earning['date'].append(date)
                        earning['time'].append(time[i - len(actual)].text)
        return json.dumps("OK")
    
    #copy data
    tickers = driver.find_elements_by_class_name('ticker')
    time_title = driver.find_element_by_id("time")
    actual_title = driver.find_element_by_id("actual")
    if time_title.is_displayed():
        for i in range (len(tickers)):       
            time = driver.find_elements_by_class_name('time')
            tickers_ = driver.find_elements_by_class_name('ticker')
            if tickers_[i].text != '':
                earning['ticker'].append(tickers_[i].text)
                earning['date'].append(date)
                earning['time'].append(time[i].text)
    elif actual_title.is_displayed():
        for i in range (len(tickers)):
            time = driver.find_elements_by_class_name('time')
            actual = driver.find_elements_by_css_selector("div[class^='actual']")
            tickers_ = driver.find_elements_by_class_name('ticker')
            if i < len(actual):
                if tickers_[i].text != '':
                    earning['ticker'].append(tickers_[i].text)
                    earning['date'].append(date)
                    earning['time'].append(actual[i].text)
            elif i >= len(actual):
                if tickers_[i].text != '':
                    earning['ticker'].append(tickers_[i].text)
                    earning['date'].append(date)
                    earning['time'].append(time[i - len(actual)].text)     
            
    return json.dumps("OK")
