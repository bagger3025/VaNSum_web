from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display
import time

def make_gsum(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    # driver로 특정 페이지를 크롤링한다.
    driver.get(url)
    try:
        if url != '':
            button = driver.find_element_by_xpath('//*[@id="main_content"]/div[1]/div[3]/div/div[3]/div[2]/div[1]/a')
            button.click()
            time.sleep(1)
            item = driver.find_element_by_xpath('//*[@id="main_content"]/div[1]/div[3]/div/div[3]/div[2]/div[1]/div/div[2]/div[1]')
            body = item.text
        else:
            body = ''
    except:
        body = ""
    finally:
        driver.quit()
        return body

def make_gsum_title(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    # driver로 특정 페이지를 크롤링한다.
    driver.get(url)
    print(type(url))
    try:
        if url != '':
            title = driver.find_element_by_xpath('//*[@id="articleTitle"]')
            title = title.text
        else:
            title = ''
    except:
        title = ""
    finally:
        driver.quit()
        return title