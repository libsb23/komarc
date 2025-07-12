import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def parse_aladin_detail_page(html):
    soup = BeautifulSoup(html, "html.parser")

    # 제목
    title_tag = soup.select_one("span.Ere_bo_title")
    title = title_tag.text.strip() if title_tag else "제목 없음"

    # li.Ere_sub2_title 내부에서 모든 텍스트와 태그를 순회하며 역할어 판별
    li_tag = soup.select_one("li.Ere_sub2_title")
    author = ""
    translator = ""
    publisher = ""
    pubyear = ""

    if li_tag:
        children = li_tag.contents
        prev_text = ""
        for i, node in enumerate(children):
            if node.name == "a":
                name = node.text.strip()
                next_text = children[i+1].strip() if i+1 < len(children) and isinstance(children[i+1], str) else ""
                if "지은이" in next_text:
                    author = name
                elif "옮긴이" in next_text:
                    translator = name
                elif re.search(r"\d{4}-\d{2}-\d{2}", next_text):
                    # 날짜가 아닌 경우 이전 name이 출판사
                    publisher = name
            elif isinstance(node, str):
                # 날짜 처리
                date_match = re.search(r"\d{4}-\d{2}-\d{2}", node)
                if date_match:
                    pubyear = date_match.group().split("-")[0]

    # 저자 표현
    if author and translator:
        creator_str = f"{author} ; {translator}"
    elif author:
        creator_str = author
    elif translator:
        creator_str = translator
    else:
        creator_str = "저자 정보 없음"

    # KORMARC 반환
    return {
        "245": f"=245  10$a{title} /$c{creator_str}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a1책."
    }

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

# Streamlit 인터페이스
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
