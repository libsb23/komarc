from bs4 import BeautifulSoup
import requests
import re

def parse_aladin_detail_page(html):
    soup = BeautifulSoup(html, "html.parser")

    # 제목
    title_tag = soup.select_one("span.Ere_bo_title")
    title = title_tag.text.strip() if title_tag else "제목 없음"

    # li 안의 모든 a 태그
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

    # 발행일 (텍스트에서 날짜만 추출)
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", texts)
    pubyear = date_match.group().split("-")[0] if date_match else "발행연도 없음"

    return {
        "245": f"=245  10$a{title} /$c{creator_str}",
        "260": f"=260  \\$a[출판지 미상] :$b{publisher},$c{pubyear}.",
        "300": f"=300  \\$a1책."
    }
