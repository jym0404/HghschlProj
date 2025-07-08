import requests
from bs4 import BeautifulSoup

def refine(soup):
    ul = soup.select_one('#mw-content-text > div.mw-content-ltr.mw-parser-output > ul:nth-of-type(1)')
    removal = ul.find_all('sup', class_='reference')
    for element in removal:
        element.decompose()
    return ul.get_text()

def crawl(month, day):

    url=f'https://ko.wikipedia.org/wiki/{month}월_{day}일'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return refine(soup)
    else:
        raise ValueError