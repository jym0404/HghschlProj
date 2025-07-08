import streamlit as st
import requests
from bs4 import BeautifulSoup

def summarize(prompt):
    return "yeet"

def refine(soup):
    ul = soup.select_one('#mw-content-text > div.mw-content-ltr.mw-parser-output > ul:nth-of-type(1)')
    removal = ul.find_all('sup', class_='reference')
    for element in removal:
        element.decompose()
    return ul.get_text()

def crawl_month_and_day(month, day):

    url=f'https://ko.wikipedia.org/wiki/{month}월_{day}일'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return refine(soup)
    else:
        raise ValueError

if 'scrapped' not in st.session_state:
    st.session_state.scrapped = None

if 'summarized' not in st.session_state:
    st.session_state.summarized = None

#st.set_page_config(layout='wide')

#_, main, _ = st.columns([1,5,1])

st.title('정유민의 개쩌는 앱')

day_by_month = {
    1:31,
    2:29,
    3:31,
    4:30,
    5:31,
    6:30,
    7:31,
    8:31,
    9:30,
    10:31,
    11:30,
    12:31
}

month_and_day, year = st.tabs(['Month and Day','Year'])

### M and D

bigcol1, bigcol2 = month_and_day.columns([3,2])

col1, col2 = bigcol1.columns(2)

month = col1.number_input("Month", 1, 12)
day = col2.number_input("Day", 1, day_by_month[month])

clicked_search = bigcol1.button("Search", use_container_width=True)

#col3, col4 = st.columns(2)

if clicked_search:
    st.session_state.scrapped = crawl_month_and_day(month,day)

out1 = bigcol1.text_area("Scrapped", value=st.session_state.scrapped, height=500)

###########

user_ask = bigcol2.text_input("Request", placeholder="긍정적인 내용 위주로 알려줘")

clicked_summarize = bigcol2.button("Summarize", use_container_width=True)

if clicked_summarize:

    prompt="""{out1}
    
    다음 글을 '{USER_ASK}'라는 유저의 요청에 맞춰 요약해줘. (공백이면 알아서 요약해줘)  
    - 요약은 바로 시작하고, 도입부에 “다음은 ~ 요약입니다.” 같은 문장은 넣지 마.  
    - 끝인사나 추가 설명도 붙이지 말고, 요약 내용만 간결하게 써줘.
    - DO NOT SAY ANYTHING EXCEPT THE SUMMARY
    - SPEAK IN KOREAN
    """

    st.session_state.summarized = summarize(prompt)

out2 = bigcol2.text_area("Summary", value=st.session_state.summarized, height=500)

######## Years