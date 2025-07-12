import requests
from bs4 import BeautifulSoup
import re

def crawl_aladin_book_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 제목
    title_tag = soup.select_one("span.Ere_bo_title")
    title = title_tag.text.strip() if title_tag else "제목 없음"

    # 저자, 역자, 그림 등
    creator_tags = soup.select("li.Ere_sub2_title a")
    creators = [tag.text.strip() for tag in creator_tags]
    creator_str = " ; ".join(creators) if creators else "저자 정보 없음"

    # 출판사 및 발행년도
    pub_info_tag = soup.select_one("li.Ere_sub_content")
    pub_text = pub_info_tag.text.strip() if pub_info_tag else ""
    
    # 출판사 / 연도 분리
    publisher = ""
    pubyear = ""
    if "/" in pub_text:
        parts = pub_text.split("/")
        publisher = parts[0].strip()
        year_match = re.search(r"\d{4}", parts[1])
        pubyear = year_match.group() if year_match else ""
    else:
        publisher = pub_text.strip()

    # 결과 정리
    return {
        "title": title,
        "creators": creator_str,
        "publisher": publisher,
        "pubyear": pubyear
    }

# 테스트용
book_url = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=331619107"
book_info = crawl_aladin_book_info(book_url)
print(book_info)
