
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
        #select amc option
        amc_option = driver.find_element_by_id("amc")
        driver.execute_script("arguments[0].setAttribute('style','display:inline;')",amc_option)
        amc_coordinates = amc_option.location
        driver.execute_script("window.scrollTo(0, arguments[0])", amc_coordinates.get('y'))
        amc_overlay = driver.find_element_by_class_name("switch-selection")
        driver.execute_script("arguments[0].style.visibility='hidden'", amc_overlay)
        amc_option.click()

        #copy data        
        tickers = driver.find_elements_by_class_name('ticker')
        for i in range (len(tickers)):
            tickers_ = driver.find_elements_by_class_name('ticker')
            if tickers_[i].text != '':
                earning['ticker'].append(tickers_[i].text)
                earning['date'].append(date)
                earning['time'].append('amc')

        #select bmo option
        bmo_option = wait.until(EC.presence_of_element_located((By.ID, "bmo")))
        driver.execute_script("arguments[0].setAttribute('style','display:inline;')",bmo_option)
        bmo_coordinates = bmo_option.location
        driver.execute_script("window.scrollTo(0, arguments[0])", bmo_coordinates.get('y'))
        bmo_overlay = driver.find_element_by_class_name("switch-selection")
        driver.execute_script("arguments[0].style.visibility='hidden'", bmo_overlay)
        bmo_option.click()

        #copy data
        tickers = driver.find_elements_by_class_name('ticker')
        for i in range (len(tickers)):
            tickers_ = driver.find_elements_by_class_name('ticker')
            if tickers_[i].text != '':
                earning['ticker'].append(tickers_[i].text)
                earning['date'].append(date)
                earning['time'].append('bmo')


    except NoSuchElementException:
        try:
            #select amc option
            amc_option = driver.find_element_by_id("amc")
            driver.execute_script("arguments[0].setAttribute('style','display:inline;')",amc_option)
            amc_coordinates = amc_option.location
            driver.execute_script("window.scrollTo(0, arguments[0])", amc_coordinates.get('y'))
            amc_overlay = driver.find_element_by_class_name("switch-selection")
            driver.execute_script("arguments[0].style.visibility='hidden'", amc_overlay)
            amc_option.click()

            #copy data        
            tickers = driver.find_elements_by_class_name('ticker')
            for i in range (len(tickers)):
                tickers_ = driver.find_elements_by_class_name('ticker')
                if tickers_[i].text != '':
                    earning['ticker'].append(tickers_[i].text)
                    earning['date'].append(date)
                    earning['time'].append('amc')

            #select bmo option
            bmo_option = wait.until(EC.presence_of_element_located((By.ID, "bmo")))
            driver.execute_script("arguments[0].setAttribute('style','display:inline;')",bmo_option)
            bmo_coordinates = bmo_option.location
            driver.execute_script("window.scrollTo(0, arguments[0])", bmo_coordinates.get('y'))
            bmo_overlay = driver.find_element_by_class_name("switch-selection")
            driver.execute_script("arguments[0].style.visibility='hidden'", bmo_overlay)
            bmo_option.click()

            #copy data
            tickers = driver.find_elements_by_class_name('ticker')
            for i in range (len(tickers)):
                tickers_ = driver.find_elements_by_class_name('ticker')
                if tickers_[i].text != '':
                    earning['ticker'].append(tickers_[i].text)
                    earning['date'].append(date)
                    earning['time'].append('bmo')
        except:
            driver.quit()
            return json.dumps("Error copying")
    return json.dumps("OK")