import pandas as pd
import openai
import streamlit as st

openai.api_key = 'sk-svcacct-bMnwMD9xWNRBqQuJBYXFT3BlbkFJgNMMno7o2G4Cf5JQRJAD'

# 데이터 파일 경로를 함수 인자로 받도록 수정
def load_gpt_df(file_path):
    return pd.read_excel(file_path)

def gpt_analysis(gpt_df):
    gpt_df['날짜'] = pd.to_datetime(gpt_df['날짜'])
    gpt_df['년도'] = gpt_df['날짜'].dt.year
    gpt_df['월'] = gpt_df['날짜'].dt.month
    gpt_df['날짜'] = pd.to_datetime(gpt_df['날짜']).dt.strftime('%Y-%m')
    data_analysis = gpt_df[gpt_df['년도'] == 2024]
    prompt = f"{data_analysis.to_string()} SIIC라는 CS 대행 서비스를 제공하는 업체의 월별 운영실적파일이야. 각 서비스 별로 전월대비 어떠한 변화가 있는지 유의미한 수치 변화가 있는지 분석해줘. 기본적으로 서비스 별로 최근 월이 전월대비 어떠한 변화가 있는지 설명해주고, 각 서비스별로 어떠한 수치적인 변화가 있는지 분석해줘. 또 인사이트가 있다면 제공해줘."
    response = ask_gpt(prompt)
    return response

def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 CS 운영실적을 분석하는 컨설턴트야."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']
