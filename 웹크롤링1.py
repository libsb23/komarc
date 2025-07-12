import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 상세페이지 파싱
def parse_aladin_detail_page(html):
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("span.Ere_bo_title")
    title = title_tag.text.strip() if title_tag else "제목 없음"

    li_tag = soup.select_one("li.Ere_sub2_title")

    author_list = []
    publisher = ""
    pubyear = ""

    if li_tag:
        children = li_tag.contents
        last_a_before_date = None

        for i, node in enumerate(children):
            if getattr(node, "name", None) == "a":
                name = node.text.strip()
                next_text = children[i+1].strip() if i+1 < len(children) and isinstance(children[i+1], str) else ""

                if "지은이" in next_text:
                    author_list.append(f"{name} 지음")
                elif "옮긴이" in next_text:
                    author_list.append(f"{name} 옮김")
                else:
                    last_a_before_date = name

            elif isinstance(node, str):
                date_match = re.search(r"\d{4}-\d{2}-\d{2}", node)
                if date_match:
                    pubyear = date_match.group().split("-")[0]
                    if last_a_before_date:
                        publisher = last_a_before_date

    creator_str = " ; ".join(author_list) if author_list else "저자 정보 없음"
    publisher = publisher if publisher else "출판사 정보 없음"
    pubyear = pubyear if pubyear else "발행연도 없음"

    return {
        "245": f"=245  10$a{title} /$c{creator_str}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a1책."
    }

# ISBN 검색 → 상세페이지 이동 → 파싱
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
st.title("📚 알라딘 KORMARC 필드 추출기 (다중 ISBN 지원)")

isbn_input = st.text_area("ISBN을 '/'로 구분하여 입력하세요:")

if isbn_input:
    isbn_list = [isbn.strip() for isbn in isbn_input.split("/") if isbn.strip()]

    for idx, isbn in enumerate(isbn_list, 1):
        st.markdown(f"### 📘 {idx}. ISBN: `{isbn}`")
        with st.spinner("검색 중..."):
            result, error = search_aladin_by_isbn(isbn)
            if error:
                st.error(f"❌ 오류: {error}")
            elif result:
                st.code(result["245"], language="text")
                st.code(result["260"], language="text")
                st.code(result["300"], language="text")
            else:
                st.warning("결과 없음")
