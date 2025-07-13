import streamlit as st
import requests

def search_publisher_info(keyword):
    url = "https://bnk.kpipa.or.kr/api/addition/pblshrInfoList"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "searchKeyword": keyword,
        "pageIndex": 1,
        "pageSize": 10
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        results = data.get("resultList", [])
        if not results:
            return "검색 결과가 없습니다."

        output = []
        for item in results:
            name = item.get("pblshrNm", "")
            ceo = item.get("ceoNm", "")
            biz_no = item.get("bizno", "")
            tel = item.get("telno", "")
            address = item.get("addr", "")
            category = item.get("bizrDtlNm", "")
            region = item.get("regionNm", "")
            output.append({
                "출판사명": name,
                "대표자명": ceo,
                "사업자번호": biz_no,
                "전화번호": tel,
                "주소": address,
                "업종": category,
                "지역": region
            })
        return output

    except Exception as e:
        return f"오류 발생: {e}"

# Streamlit UI
st.title("📚 출판사 정보 검색기 (BeautifulSoup 없이)")

keyword = st.text_input("🔍 출판사명을 입력하세요:")

if keyword:
    result = search_publisher_info(keyword)
    if isinstance(result, str):
        st.error(result)
    else:
        for i, item in enumerate(result, 1):
            st.markdown(f"### 결과 {i}")
            for key, value in item.items():
                st.write(f"**{key}**: {value}")
