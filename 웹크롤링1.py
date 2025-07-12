import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 상세페이지 파싱 함수
def parse_aladin_detail_page(html):
    soup = BeautifulSoup(html, "html.parser")

    # 제목
    title_tag = soup.select_one("span.Ere_bo_title")
    title = title_tag.text.strip() if title_tag else "제목 없음"

    # li 안의 a 태그와 텍스트
    li_tag = soup.select_one("li.Ere_sub2_title")
    a_tags = li_tag.select("a.Ere_sub2_title") if li_tag else []
    texts = li_tag.get_text(" ", strip=True) if li_tag else ""

    # 저자 및 옮긴이
    creators = []
    if len(a_tags) >= 2:
        creators = [a_tags[0].text.strip(), a_tags[1].text.strip()]
    elif a_tags:
        creators = [a.text.strip() for a in a_tags]
    creator_str = " ; ".join(creators) if creators else "저자 정보 없음"

    # 출판사
    publisher = a_tags[2].text.strip() if len(a_tags) >= 3 else "출판사 정보 없음"

    # 발행일
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", texts)
    pubyear = date_match.group().split("-")[0] if date_match else "발행연도 없음"

    return {
        "245": f"=245  10$a{title} /$c{creator_str}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a1책."
    }

# ISBN으로 상세페이지 이동
def search_aladin_by_isbn(isbn):
    search_url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchWord={isbn}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(search_url, headers=headers)
        if res.status_code != 200:
            return None, f"검색 실패 (status {res.status_code})"

        soup = BeautifulSoup(res.text, "html.parser")
        link_tag = soup.select_one("div.ss_book_box a.bo3")
        if not link_tag or not link_tag.get("href"):
            return None, "도서 링크를 찾을 수 없습니다."

        detail_url = link_tag["href"]
        detail_res = requests.get(detail_url, headers=headers)
        if detail_res.status_code != 200:
            return None, f"상세페이지 요청 실패 (status {detail_res.status_code})"

        result = parse_aladin_detail_page(detail_res.text)
        return result, None

    except Exception as e:
        return None, f"예외 발생: {str(e)}"

# Streamlit 앱 UI
st.title("📚 알라딘 KORMARC 필드 추출기")

isbn = st.text_input("ISBN을 입력하세요:")

if isbn:
    with st.spinner("도서 정보를 불러오는 중..."):
        result, error = search_aladin_by_isbn(isbn)

        if error:
            st.error(f"❌ 오류 발생: {error}")
        elif result:
            st.subheader("📄 KORMARC 필드 출력")
            st.code(result["245"], language="text")
            st.code(result["260"], language="text")
            st.code(result["300"], language="text")
        else:
            st.warning("도서 정보를 찾을 수 없습니다.")
