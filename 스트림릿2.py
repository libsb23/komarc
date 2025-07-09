import streamlit as st

# 타이틀
st.title("📘 간단한 Streamlit 앱")

# 입력 받기
user_input = st.text_input("텍스트를 입력하세요:")

# 버튼을 눌렀을 때 처리
if st.button("출력하기"):
    if user_input:
        st.success(f"당신이 입력한 내용: {user_input}")
    else:
        st.warning("아무것도 입력하지 않았어요.")
