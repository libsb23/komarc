# streamlit_aladin_kormarc.py

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def search_aladin_kormarc(isbn):
    url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={isbn}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "요청 실패"

    soup = BeautifulSoup(response.text, "html.parser")
    item = soup.select_one(".ss_book_box")
    if not item:
        return "검색 결과 없음"

    title = item.select_one(".bo3").text.strip() if item.select_one(".bo3") else "제목 없음"
    author_info = item.select_one(".ss_book_list").text.strip() if item.select_one(".ss_book_list") else ""

    # 출판사 및 연도 추출
    publisher_match = re.search(r'/\s*([^:]+)\s*:', author_info)
    year_match = re.search(r'(\d{4})', author_info)

    publisher = publisher_match.group(1).strip() if publisher_match else "출판사 정보 없음"
    pubyear = year_match.group(1) if year_match else "발행연도 없음"

    # 요약 정보를 페이지 수처럼 가공 (300필드 대용)
    description = item.select_one(".ss_ht1").text.strip() if item.select_one(".ss_ht1") else ""
    page_info = f"{len(description)}자 분량 요약" if description else "형태 정보 없음"

    return {
        "245": f"=245  10$a{title} /$c{author_info}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a{page_info}."
    }

# Streamlit 인터페이스
st.title("📚 KORMARC 형식 변환기 (ISBN 기반)")

isbn_input = st.text_input("ISBN을 입력하세요:")

if isbn_input:
    with st.spinner("검색 중입니다..."):
        result = search_aladin_kormarc(isbn_input)
        if isinstance(result, dict):
            st.subheader("📄 KORMARC 필드 출력")
            st.code(result["245"])
            st.code(result["260"])
            st.code(result["300"])
        else:
            st.warning(result)
