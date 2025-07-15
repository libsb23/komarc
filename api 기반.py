import streamlit as st
import requests
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔹 발행국 부호 구하기 (구글 시트 Sheet2 활용)
def get_country_code_by_region(region_name):
    try:
        st.write(f"🌍 발행국 부호 찾는 중... 참조 지역: `{region_name}`")

        json_key = dict(st.secrets["gspread"])
        json_key["private_key"] = json_key["private_key"].replace('\\n', '\n')

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
        client = gspread.authorize(creds)
        sheet = client.open("출판사 DB").worksheet("Sheet2")

        region_col = sheet.col_values(1)[1:]
        code_col = sheet.col_values(2)[1:]

        def normalize_region(region):
            region = region.strip()
            was_teukbyeol = "특별자치도" in region
            region = re.sub(r"(광역시|특별시|특별자치도)", "", region)
            if region in ["강원도", "제주도", "경기도"]:
                return region.replace("도", "")
            if region.endswith("도") and len(region) >= 4 and not was_teukbyeol:
                return region[0] + region[2]
            if region.endswith("시"):
                return region[:-1]
            return region

        normalized_input = normalize_region(region_name)
        st.write(f"🧪 정규화된 참조지역: `{normalized_input}`")

        for sheet_region, country_code in zip(region_col, code_col):
            if normalize_region(sheet_region) == normalized_input:
                return country_code.strip() or "xxu"

        return "xxu"

    except Exception:
        return "xxu"

# 🔹 Google Sheets에서 지역명 추출
def get_publisher_location(publisher_name):
    try:
        st.write(f"📥 출판사 지역을 구글 시트에서 찾는 중입니다... `{publisher_name}`")

        json_key = dict(st.secrets["gspread"])
        json_key["private_key"] = json_key["private_key"].replace('\\n', '\n')

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
        client = gspread.authorize(creds)
        sheet = client.open("출판사 DB").worksheet("Sheet1")

        publisher_names = sheet.col_values(2)[1:]
        regions = sheet.col_values(3)[1:]

        def normalize(name):
            return re.sub(r"\s|\(.*?\)|주식회사|㈜|도서출판|출판사", "", name).lower()

        target = normalize(publisher_name)
        st.write(f"🧪 정규화된 입력값: `{target}`")

        for sheet_name, region in zip(publisher_names, regions):
            if normalize(sheet_name) == target:
                return region.strip() or "출판지 미상"

        for sheet_name, region in zip(publisher_names, regions):
            if sheet_name.strip() == publisher_name.strip():
                return region.strip() or "출판지 미상"

        return "출판지 미상"

    except Exception:
        return "예외 발생"

# 🔹 알라딘 API 기반 데이터 통합 파싱
def search_aladin_by_isbn(isbn):
    try:
        ttbkey = st.secrets["aladin"]["ttbkey"]
        url = "https://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
        params = {
            "ttbkey": ttbkey,
            "itemIdType": "ISBN",
            "ItemId": isbn,
            "output": "js",
            "Version": "20131101"
        }

        res = requests.get(url, params=params)
        if res.status_code != 200:
            return None, f"API 요청 실패 (status: {res.status_code})"

        data = res.json()
        if "item" not in data or not data["item"]:
            return None, f"도서 정보를 찾을 수 없습니다. [응답 내용: {data}]"

        book = data["item"][0]

        title = book.get("title", "제목 없음")
        author = book.get("author", "")
        publisher = book.get("publisher", "출판사 정보 없음")
        pubdate = book.get("pubDate", "")
        pubyear = pubdate[:4] if len(pubdate) >= 4 else "발행년도 없음"

        authors = [a.strip() for a in author.split(",")]
        creator_str = " ; ".join(authors) if authors else "저자 정보 없음"

        field_245 = f"=245  10$a{title} /$c{creator_str}"
        field_300 = "=300  \\$a1책."

        return {
            "title": title,
            "creator": creator_str,
            "publisher": publisher,
            "pubyear": pubyear,
            "245": field_245,
            "300": field_300
        }, None

    except Exception as e:
        return None, f"API 예외 발생: {str(e)}"

# 🔹 Streamlit UI
st.title("📚 ISBN → API → KORMARC 변환기")

isbn_input = st.text_area("ISBN을 '/'로 구분하여 입력하세요:")

if isbn_input:
    isbn_list = [re.sub(r"[^\\d]", "", isbn) for isbn in isbn_input.split("/") if isbn.strip()]

    for idx, isbn in enumerate(isbn_list, 1):
        st.markdown(f"---\n### 📘 {idx}. ISBN: `{isbn}`")
        with st.spinner("🔍 도서 정보 검색 중..."):
            result, error = search_aladin_by_isbn(isbn)

        if error:
            st.error(f"❌ 오류: {error}")
            continue

        if result:
            publisher = result["publisher"]
            pubyear = result["pubyear"]

            st.code(result["245"], language="text")

            if publisher == "출판사 정보 없음":
                location = "[출판지 미상]"
            else:
                with st.spinner(f"📍 '{publisher}'의 지역정보 검색 중..."):
                    location = get_publisher_location(publisher)

            if publisher != "출판사 정보 없음":
                st.info(f"🏙️ 지역정보 결과: **{location}**")

            field_260 = f"=260  \\$a{location} :$b{publisher},$c{pubyear}."
            st.code(field_260, language="text")
            st.code(result["300"], language="text")

            country_code = get_country_code_by_region(location)
            st.code(f"=008  \\$a{country_code}", language="text")

        else:
            st.warning("결과 없음")
