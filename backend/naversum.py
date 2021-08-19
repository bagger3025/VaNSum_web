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


# from kogi
def load_summary_from_url(url):
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    time.sleep(2)

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)

    try:
        driver.find_element_by_xpath('//a[@class="media_end_head_autosummary_button _toggle_btn nclicks(sum_summary)"]').click()

        time.sleep(1)

        summary = driver.find_element_by_xpath('//div[@class="_contents_body"]')
        body = summary.text
    except:
        body = ""
        pass
    finally:
        driver.quit()

    display.stop()

    return body

a = load_summary_from_url("https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid1=103&oid=422&aid=0000497494")
print(a)