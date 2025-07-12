import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def crawl_aladin_book_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return None, f"상세 페이지 요청 실패: status code {res.status_code}"

        soup = BeautifulSoup(res.text, "html.parser")

        # 제목
        title_tag = soup.select_one("span.Ere_bo_title")
        title = title_tag.text.strip() if title_tag else None
        if not title:
            return None, "제목을 찾을 수 없습니다 (span.Ere_bo_title 선택 실패)"

        # 저자 / 역자
        creator_tags = soup.select("li.Ere_sub2_title a")
        creators = [tag.text.strip() for tag in creator_tags]
        creator_str = " ; ".join(creators) if creators else None
        if not creator_str:
            return None, "저자 정보를 찾을 수 없습니다 (li.Ere_sub2_title > a 선택 실패)"

        # 출판사 및 발행연도
        pub_info_tag = soup.select_one("li.Ere_sub_content")
        if not pub_info_tag:
            return None, "출판사 정보를 찾을 수 없습니다 (li.Ere_sub_content 선택 실패)"

        pub_text = pub_info_tag.text.strip()
        publisher = ""
        pubyear = ""

        if "/" in pub_text:
            parts = pub_text.split("/")
            publisher = parts[0].strip()
            year_match = re.search(r"\d{4}", parts[1])
            pubyear = year_match.group() if year_match else ""
        else:
            publisher = pub_text.strip()

        result = {
            "245": f"=245  10$a{title} /$c{creator_str}",
            "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
            "300": f"=300  \\$a1책."
        }
        return result, None

    except Exception as e:
        return None, f"예외 발생: {str(e)}"

def search_aladin_by_isbn(isbn):
    search_url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchWord={isbn}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(search_url, headers=headers)
        if res.status_code != 200:
            return None, f"검색 페이지 요청 실패: status code {res.status_code}"

        soup = BeautifulSoup(res.text, "html.parser")
        link_tag = soup.select_one("div.ss_book_box a.bo3")
        if not link_tag or not link_tag.get("href"):
            return None, "도서 상세 링크를 찾을 수 없습니다 (a.bo3 선택 실패)"

        detail_url = link_tag["href"]
        return crawl_aladin_book_info(detail_url)

    except Exception as e:
        return None, f"예외 발생: {str(e)}"

# Streamlit UI
st.title("📚 알라딘 KORMARC 필드 추출기")

isbn = st.text_input("ISBN을 입력하세요:")

if isbn:
    with st.spinner("검색 중입니다..."):
        result, error = search_aladin_by_isbn(isbn)
        if error:
            st.error(f"❌ 오류 발생: {error}")
        elif result:
            st.subheader("📄 KORMARC 필드")
            st.text(result["245"])
            st.text(result["260"])
            st.text(result["300"])
        else:
            st.warning("도서 정보를 가져오지 못했습니다.")
