import streamlit as st
import requests
from bs4 import BeautifulSoup
import ollama
import base64
import zstandard as zstd

anniversaries = {
    (1, 1): "새해 (신정)",
    (3, 1): "삼일절",
    (5, 5): "어린이날",
    (6, 6): "현충일",
    (8, 15): "광복절",
    (10, 3): "개천절",
    (10, 9): "한글날",
    (12, 25): "크리스마스",
    (2, 14): "발렌타인데이",
    (4, 22): "지구의 날",
    (5, 1): "근로자의 날",
    (6, 5): "환경의 날",
    (7, 17): "제헌절"
}

MODEL_LIST=['gemma3:4b-it-q4_K_M']

def summarize(out1, user_ask):
    prompt=f"""{out1}
    
    다음 글을 '{user_ask}'라는 유저의 요청에 맞춰 요약해줘.   
    - 끝인사나 추가 설명도 붙이지 말고, 요약 내용만 간결하게 써줘.
    - 서론 없이 본문만을 줄바꿈을 적절히 사용하여 작성해줘
    - 요약은 바로 시작하고, 도입부에 “다음은 ~ 요약입니다.” 같은 문장은 넣지 마. 
    - ONLY SAY THE SUMMARY
    - SPEAK IN KOREAN
    """

    response = ollama.chat(model=MODEL_LIST[0], messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])

    return response['message']['content']

def refine_month_and_day(soup):
    result = BeautifulSoup("", "html.parser").new_tag("div")
    result.append(soup.select_one('#mw-content-text > div.mw-content-ltr.mw-parser-output > ul:nth-of-type(1)'))
    result.append(BeautifulSoup("", "html.parser").new_tag("br"))
    result.append(soup.select_one('#mw-content-text > div.mw-content-ltr.mw-parser-output > ul:nth-of-type(1)'))
    removal = result.find_all('sup', class_='reference')
    for element in removal:
        element.decompose()
    return result.get_text()

def crawl_month_and_day(month, day):

    if (month, day) in anniversaries:
        result = f"기념일 : {anniversaries[(month, day)]}\n\n"

    url=f'https://ko.wikipedia.org/wiki/{month}월_{day}일'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        result += refine_month_and_day(soup)
    else:
        raise ValueError
    return result

if 'scrapped_mnd' not in st.session_state:
    st.session_state.scrapped_mnd = None

if 'summarized_mnd' not in st.session_state:
    st.session_state.summarized_mnd = None


if 'scrapped_cent' not in st.session_state:
    st.session_state.scrapped_cent = None

if 'summarized_cent' not in st.session_state:
    st.session_state.summarized_cent = None

#st.set_page_config(layout='wide')

#_, main, _ = st.columns([1,5,1])

title, helper = st.columns([20,1])

title.title('시간 탐색기')
#helper.download_button('?', use_container_width=True)

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

month_and_day, century = st.tabs(['Month and Day', 'Century'])

###-------------------------------- M and D

bigcol1_mnd, bigcol2_mnd = month_and_day.columns([1,1])

col1_mnd, col2_mnd = bigcol1_mnd.columns(2)

month = col1_mnd.number_input("Month", 1, 12)
day = col2_mnd.number_input("Day", 1, day_by_month[month])

clicked_search = bigcol1_mnd.button("Search", use_container_width=True)

#col3, col4 = st.columns(2)

if clicked_search and month <= 12 and day <= day_by_month[month]:
    st.session_state.scrapped_mnd = crawl_month_and_day(month,day)

out1 = bigcol1_mnd.text_area("Scrapped", value=st.session_state.scrapped_mnd, height=500)

###########

user_ask = bigcol2_mnd.text_input("Request", placeholder="어떻게 요약할까요?")

clicked_summarize = bigcol2_mnd.button("Summarize", use_container_width=True)

if clicked_summarize:

    st.session_state.summarized_mnd = summarize(out1, user_ask)

out2 = bigcol2_mnd.text_area("Summary", value=st.session_state.summarized_mnd, height=500)

########--------------------------------- Year
def refine_century(soup):
    #ul = soup.select_one('#mw-content-text > div.mw-content-ltr.mw-parser-output > ul:nth-of-type(1)')
    inner = soup.select_one('#bodyContent')
    removal = inner.find_all('sup', class_='reference')
    for element in removal:
        element.decompose()
    removal = inner.find_all('span', class_='mw-editsection')
    for element in removal:
        element.decompose()
    if inner.find('table', class_='infobox'): inner.find('table', class_='infobox').decompose()
    if inner.find('table'): inner.find('table').decompose()
    if inner.find('div', class_='reflist'): inner.find('div', class_='reflist').decompose()
    if inner.find('div', class_='navbox'): inner.find('div', class_='navbox').decompose()
    if inner.find('div', class_='navbox'): inner.find('div', class_='navbox').decompose()
    return inner.get_text().replace('위키백과, 우리 모두의 백과사전.','').replace('\n\n','\n').split('원본 주소')[0]

def crawl_century(cent, is_bc):

    url=f'https://ko.wikipedia.org/wiki/{'기원전_' if is_bc else ''}{cent}세기'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return refine_century(soup)
    else:
        raise ValueError

bigcol1_cent, bigcol2_cent = century.columns([1,1])

col1_cent, col2_cent = bigcol1_cent.columns([1,2])
is_bc = col1_cent.selectbox('',['BC','AD'], index=1) == 'BC'
cent = col2_cent.number_input('Centuries', min_value=1, max_value=None if is_bc else 21)

clicked_search_cent = bigcol1_cent.button("Search", use_container_width=True, key=158)

#col3, col4 = st.columns(2)

if clicked_search_cent:
    st.session_state.scrapped_cent = crawl_century(cent, is_bc)

out1_cent = bigcol1_cent.text_area("Scrapped Century", value=st.session_state.scrapped_cent, height=500)

###########

user_ask_cent = bigcol2_cent.text_input("Request", placeholder="어떻게 요약할까요?", key=130)

clicked_summarize_cent = bigcol2_cent.button("Summarize", use_container_width=True, key=999)

if clicked_summarize_cent:

    st.session_state.summarized_cent = summarize(out1_cent, user_ask_cent)

out2_cent = bigcol2_cent.text_area("Summary Century", value=st.session_state.summarized_cent, height=500)