import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 크롬 드라이버 설정
@st.cache_resource
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # GUI 없이 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def search_publisher(publisher_name):
    driver = get_driver()
    driver.get("https://bnk.kpipa.or.kr/home/v3/addition/adiPblshrInfoList")
    time.sleep(3)  # 페이지 로딩 대기

    try:
        # 검색창 찾기 및 검색어 입력
        search_box = driver.find_element(By.ID, "searchKeyword")
        search_box.clear()
        search_box.send_keys(publisher_name)
        search_box.send_keys(Keys.RETURN)

        time.sleep(2)  # 검색 결과 대기

        # 검색 결과 추출
        results = driver.find_elements(By.CSS_SELECTOR, "#pblshrListBody > tr")
        if not results:
            return "검색 결과가 없습니다."

        data = []
        for result in results:
            cols = result.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:
                name = cols[0].text.strip()
                area = cols[2].text.strip()
                category = cols[3].text.strip()
                data.append((name, area, category))
        
        return data

    except Exception as e:
        return f"오류 발생: {e}"

# Streamlit UI
st.title("출판사 정보 검색기")
publisher_name = st.text_input("출판사명을 입력하세요:")

if publisher_name:
    st.write(f"🔍 '{publisher_name}' 검색 결과:")
    results = search_publisher(publisher_name)
    if isinstance(results, str):
        st.error(results)
    else:
        for name, area, category in results:
            st.success(f"📚 출판사명: {name}\n📍 지역: {area}\n📂 업종: {category}")
