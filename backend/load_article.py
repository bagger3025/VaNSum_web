import requests
import re as re1
from bs4 import BeautifulSoup

from pyvirtualdisplay import Display
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def load_article_from_url(url):
    if not url.startswith('https://news.naver.com'):
        return {"body": 'This is not an url from Naver news'}

    re = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = BeautifulSoup(re.text, 'html.parser')
    news = html.find('meta', property='me2:category1')['content']
    body = clean_body(html.select_one('#articleBodyContents'), news)

    bodyBracketReplaced = re1.sub(r'\([^)]*\)', '', body)
    splitted = bodyBracketReplaced.split("<br/>")
    
    return splitted

def clean_body(body, news):
    result = ""
    br = False
    newcontents = []
    for ct in body.contents:
        if ct.name == 'div':
            newcontents.extend(ct.contents)
        else:
            newcontents.append(ct)
    for item in newcontents:
        stripped = str(item).replace("<div>", "").replace("</div>", "").replace("\xa0", " ").strip()
        if stripped == "":
            continue
        if stripped[0] not in ["<","/"]:
            result += stripped
            br = True
        if (stripped == "<br/>") and br:
            result += stripped
            br = False
    # print(result)
    result = re1.sub(' {2,}', " ", result)
    result = result.replace("&apos;", "")
    result = result.replace(u"\u201c", '"')
    result = result.replace(u"”", "\"")
    result = result.replace(u"‘", "'")
    result = result.replace(u"’", "'")
    result = result[11:]
    if result.startswith("<br/>"):
        result = result[5:]
    if result.endswith("<br/>"):
        result = result[:-5]

    # Case 1: 앞은 ']' 까지 자르고 뒤은 마지막 '다.' 이후 자르기
    case1 = ['이데일리','미디어오늘','프레시안','경향신문','머니투데이','서울경제','아시아경제','헤럴드경제','더팩트','미디어오늘','아이뉴스24','오마이뉴스','디지털데일리','디지털타임스','블로터']

    # Case 2: 처음에 있는 '= ' 까지 자르기
    case2 = ['뉴시스','연합뉴스','뉴스1']

    # Case 3: 앞에  '】 ' 있으면 '】 ' 까지 자르고 뒤은 마지막 '다.' 이후 자르기
    case3 = ['파이낸셜뉴스']

    # Case 4: YTN - ※ '당신의 제보가 뉴스가 됩니다' YTN은 여러분의 소중한 제보를 기다립니다. 가 있으면 먼저 자르고 마지막 '다.' 이후 자르기
    case4 = ['YTN']

    start = 0
    end = -1
    if news in case1:
        start = result.find(']')
        end = result.rfind('다.')
    elif news in case2:
        start = result.find('= ') + 1
        end = result.rfind('다.')
    elif news in case3:
        start = result.find('】') + 1
        end = result.rfind('다.')
    elif news in case4:
        flag = result.find('※ ')
        if not flag == -1:
            result = result[:flag]
        end = result.rfind('다.')
    else:
        if result.startswith('('):
            start = result.find(')')
        elif result.startswith('['):
            start = result.find(']')
        elif result.startswith('◆'):
            start = result.find('◆', 1)
        end = result.rfind('다.')

    if start == 0:
        result = result[:end+2]
    else:
        result = result[start+1:end+2]

    if result.startswith("<br/>"):
        result = result[5:]
    if result.endswith("<br/>"):
        result = result[:-5]
    result = result.strip()

    return result

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
    
    body = clean_body_mk(body)

    bodyBracketReplaced = re1.sub(r'\([^)]*\)', '', body)
    splitted = [t.strip() for t in bodyBracketReplaced.split("\n") if t.strip() != ""]
    
    return splitted

def clean_body_mk(body):

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