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

    # 245 $a: 제목
    title = item.select_one(".bo3").text.strip() if item.select_one(".bo3") else "제목 없음"

    # 245 $c: 저자, 그린이, 옮긴이만 추출
    author_info_raw = item.select_one(".ss_book_list").text.strip() if item.select_one(".ss_book_list") else ""
    author_lines = [line.strip() for line in author_info_raw.split('\n') if line.strip()]
    author_line = author_lines[0] if author_lines else "저자 정보 없음"

    # 출판사 및 연도
    publisher_match = re.search(r'/\s*([^:]+)\s*:', author_info_raw)
    year_match = re.search(r'(\d{4})', author_info_raw)
    publisher = publisher_match.group(1).strip() if publisher_match else "출판사 정보 없음"
    pubyear = year_match.group(1) if year_match else "발행연도 없음"

    # 300 필드: 설명 길이를 형태로 변환
    description = item.select_one(".ss_ht1").text.strip() if item.select_one(".ss_ht1") else ""
    page_info = f"{len(description)}자 분량 요약" if description else "형태 정보 없음"

    return {
        "245": f"=245  10$a{title} /$c{author_line}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a{page_info}."
    }

# Streamlit UI
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
