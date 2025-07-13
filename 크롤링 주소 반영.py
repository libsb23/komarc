import streamlit as st
import gspread
import json
import re
from oauth2client.service_account import ServiceAccountCredentials

def get_publisher_location(publisher_name):
    try:
        # Streamlit secrets에서 서비스 계정 정보 읽기
        json_key = st.secrets["gspread"]
        creds_dict = {key: json_key[key] for key in json_key}
        creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sheet = client.open("출판사 DB").worksheet("Sheet1")
        publisher_names = sheet.col_values(2)[1:]
        regions = sheet.col_values(3)[1:]

        def normalize(name):
            return re.sub(r"\s|\(.*?\)|주식회사|㈜|도서출판|출판사", "", name).lower()

        target = normalize(publisher_name)

        for sheet_name, region in zip(publisher_names, regions):
            if normalize(sheet_name) == target:
                return region.strip() or "출판지 미상"

        return "출판지 미상"

    except Exception as e:
        return f"예외 발생: {str(e)}"
