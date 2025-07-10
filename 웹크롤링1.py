import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def fetch_aladin_detail(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return "상세 페이지 요청 실패"

    soup = BeautifulSoup(res.text, "html.parser")

    # 제목
    title_tag = soup.select_one("//*[@id="Ere_prod_allwrap"]/div[3]/div[2]/div[1]/div/ul/li[2]/div/span")
    title = title_tag.text.strip() if title_tag else "제목 없음"

    # 저자/옮긴이 등
    creators_tags = soup.select("#Ere_prod_allwrap > div.Ere_prod_topwrap > div.Ere_prod_titlewrap > div.left > div > ul > li.Ere_sub2_title > a:nth-child(1)")
    creators = [c.text.strip() for c in creators_tags] if creators_tags else ["저자 정보 없음"]
    creators_text = " ; ".join(creators)

    # 출판사 및 발행연도
    pub_tag = soup.select_one("s#Ere_prod_allwrap > div.Ere_prod_topwrap > div.Ere_prod_titlewrap > div.left > div > ul > li.Ere_sub2_title > a:nth-child(5)")
    pub_text = pub_tag.text.strip() if pub_tag else ""
    # 출판사와 연도 분리 (예: "문학동네, 2023")
    publisher = ""
    pubyear = ""
    if "," in pub_text:
        parts = pub_text.split(",")
        publisher = parts[0].strip()
        pubyear = parts[1].strip()
    else:
        publisher = pub_text

    # 형태사항 (300필드) - 쪽수 등 확인해서 크롤링 필요하면 여기에 추가
    physical_desc = "1책"  # 일단 기본값

    return {
        "245": f"=245  10$a{title} /$c{creators_text}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a{physical_desc}."
    }

def search_by_isbn(isbn):
    # 알라딘 상세페이지는 ISBN 검색 후 첫번째 결과의 상세페이지로 이동
    search_url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchWord={isbn}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    if res.status_code != 200:
        return "검색 페이지 요청 실패"

    soup = BeautifulSoup(res.text, "html.parser")
    first_link = soup.select_one(".bo3")
    if not first_link or not first_link.get("href"):
        return "도서 상세페이지 링크를 찾을 수 없습니다."

    detail_url = first_link["href"]
    return fetch_aladin_detail(detail_url)

st.title("📚 알라딘 상세 페이지 KORMARC 크롤러 (ISBN)")

isbn = st.text_input("ISBN을 입력하세요:")

if isbn:
    with st.spinner("검색 중..."):
        result = search_by_isbn(isbn)
        if isinstance(result, dict):
            st.subheader("KORMARC 필드 출력")
            st.text(result["245"])
            st.text(result["260"])
            st.text(result["300"])
        else:
            st.warning(result)
