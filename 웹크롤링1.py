# streamlit_aladin_crawler.py

import streamlit as st
import requests
from bs4 import BeautifulSoup

def search_aladin(isbn):
    # 알라딘 통합검색 URL
    url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={isbn}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "요청 실패"

    soup = BeautifulSoup(response.text, "html.parser")
    
    # 결과 도서 정보 찾기
    item = soup.select_one(".ss_book_box")
    if not item:
        return "검색 결과 없음"

    title = item.select_one(".bo3").text.strip() if item.select_one(".bo3") else "제목 없음"
    author_info = item.select_one(".ss_book_list").text.strip() if item.select_one(".ss_book_list") else "저자 정보 없음"
    description = item.select_one(".ss_ht1").text.strip() if item.select_one(".ss_ht1") else "설명 없음"

    return {
        "제목": title,
        "저자/출판": author_info,
        "요약": description
    }

# Streamlit 인터페이스
st.title("📚 알라딘 ISBN 검색기")
isbn_input = st.text_input("ISBN을 입력하세요:")

if isbn_input:
    with st.spinner("검색 중입니다..."):
        result = search_aladin(isbn_input)
        if isinstance(result, dict):
            st.subheader("검색 결과")
            st.write(f"**제목**: {result['제목']}")
            st.write(f"**저자/출판 정보**: {result['저자/출판']}")
            st.write(f"**요약 설명**: {result['요약']}")
        else:
            st.warning(result)
