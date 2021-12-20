import re as re1

from pyvirtualdisplay import Display
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def load_article_from_url_mk(url):
    if not url.startswith('https://vip.mk.co.kr/newSt/news/news_view2.php?'):
        return {"body": 'This is not an url from MK Report, should start with [https://vip.mk.co.kr/newSt/news/news_view2.php]'}

    display = Display(visible=0, size=(1920, 1080))
    display.start()

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)

    # driver로 특정 페이지를 크롤링한다.
    driver.get(url)
    try:
        if url != '':
            item = driver.find_element_by_xpath('//*[@id="Conts"]')
            body = item.text
        else:
            body = ''
    except:
        body = ""
    finally:
        driver.quit()
    
    body = clean_body(body)

    bodyBracketReplaced = re1.sub(r'\([^)]*\)', '', body)
    splitted = [t.strip() for t in bodyBracketReplaced.split("\n") if t.strip() != ""]
    
    return splitted

def clean_body(body):

    result = re1.sub(' {2,}', " ", body)
    result = result.replace("&apos;", "")
    result = result.replace(u"\u201c", '"')
    result = result.replace(u"”", "\"")
    result = result.replace(u"‘", "'")
    result = result.replace(u"’", "'")

    result = result.strip()

    return result

def clean_summary(text):
    result = text.replace("\n\n", " ")

    return result
