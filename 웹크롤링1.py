import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_book_info_from_detail(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "도서 상세 페이지 요청 실패"

    soup = BeautifulSoup(response.text, "html.parser")

    # 245 $a: 제목
    title_tag = soup.select_one("span.Ere_bo_title")
    title = title_tag.text.strip() if title_tag else "제목 없음"

    # 245 $c: 저자/옮긴이/그린이
    creators = soup.select("li.Ere_sub2_title")
    creators_text = " ; ".join([c.text.strip() for c in creators]) if creators else "저자 정보 없음"

    # 260과 300 필드 대체용 (간단 처리)
    publisher_info_tag = soup.select_one("span.Ere_pub")
    publisher_info = publisher_info_tag.text.strip() if publisher_info_tag else ""
    
    # 출판사, 연도 분리
    publisher = publisher_info.split(",")[0].strip() if "," in publisher_info else publisher_info
    pubyear = publisher_info.split(",")[1].strip() if "," in publisher_info else "발행연도 없음"

    # 300 필드 (간단히 "1책"으로 표현)
    physical = "1책"

    return {
        "245": f"=245  10$a{title} /$c{creators_text}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a{physical}."
    }

def search_aladin(isbn):
    search_url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={isbn}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return "검색 요청 실패"

    soup = BeautifulSoup(response.text, "html.parser")
    # 첫 번째 도서 상세 페이지 링크 추출
    link_tag = soup.select_one(".bo3")
    if not link_tag or not link_tag.get("href"):
        return "도서 링크를 찾을 수 없습니다"

    detail_url = link_tag["href"]
    return extract_book_info_from_detail(detail_url)

# Streamlit 인터페이스
st.title("📚 KORMARC 필드 추출기 (ISBN 기반)")

isbn_input = st.text_input("ISBN을 입력하세요:")

def show_kormarc_line(field: str):
    st.markdown(f"<pre style='white-space:pre-wrap; word-break:break-all; font-family:monospace'>{field}</pre>", unsafe_allow_html=True)

if isbn_input:
    with st.spinner("검색 중입니다..."):
        result = search_aladin(isbn_input)
        if isinstance(result, dict):
            st.subheader("📄 KORMARC 필드 출력")
            show_kormarc_line(result["245"])
            show_kormarc_line(result["260"])
            show_kormarc_line(result["300"])

            

        else:
            st.warning(result)


