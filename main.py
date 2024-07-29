import streamlit as st
from datetime import datetime
import mall_daycall  # 모듈을 import

# 사이드바에 탭 추가
st.sidebar.title('SIIC Data platform')

# Main tabs
main_tabs = ["READ ME","SIIC Management", "SIIC Reporting"]
main_selected_tab = st.sidebar.radio("Select a category", main_tabs)

if main_selected_tab == "READ ME":
    st.info("SIIC Data Platform은 데이터를 손쉽게 조작하고 다운로드할 수 있는 기능을 제공하며, 운영 지원을 위한 데이터 분석을 지원합니다.")    

elif main_selected_tab == "SIIC Management":
    sub_tabs = ["SIIC 운영현황", "SIIC 운영실적", "SIIC 수요예측"]
    sub_selected_tab = st.sidebar.radio("SIIC Management", sub_tabs)

    if sub_selected_tab == "SIIC 운영현황":
        st.header("SIIC 운영현황")

    elif sub_selected_tab == "SIIC 운영실적":
        st.header("SIIC 운영실적")
        st.write("SIIC 콜 처리 현황입니다.")
        st.write(" :green[*raw data*]는 :blue[*csv 파일*]로 다운로드 가능합니다.")
        '''
        ---
        '''
        df_daycall = mall_daycall.load_and_prepare_data('pusan_mall_2024-07-22.csv')
        
        # raw data
        # st.dataframe(df_daycall)
        
        # 탭 생성
        c1, c2, c3 = st.tabs(['전체 콜 현황','부서별', '업체별'])
        
        # 월별 선차트
        with c1:
            c1.info('2024년도 "콜 현황 조회" 입니다')
            mall_daycall.plot_daycall_charts(df_daycall)
        
        mall_name = df_daycall['쇼핑몰명'].unique()
        team_name = df_daycall['팀명'].unique()
        
        with c2:
            st.info('부서별 "콜 상세 현황 조회" 입니다.')
            mall_daycall.display_team_data(df_daycall, team_name)
        
        with c3:
            st.info('업체별 "콜 상세 현황 조회" 입니다.')
            mall_daycall.display_mall_data(df_daycall, mall_name)

    elif sub_selected_tab == "SIIC 수요예측":
        st.subheader("SIIC 콜 처리량 수요예측")
        st.info('5년간의 콜 처리 데이터를 기반으로 모델을 학습하여 향후 7개월 동안의 콜 처리량을 예측하였습니다. 2024년 1월부터 6월까지의 실제값과 예측값 간의 정확도를 MAPE 기준으로 측정한 결과, 현재 모형의 예측 성능은 94.7% 입니다.')
        call_forecast()

elif main_selected_tab == "SIIC Reporting":
    sub_tabs = ["SIIC 월간보고", "SIIC 일간보고"]
    sub_selected_tab = st.sidebar.radio("SIIC Reporting", sub_tabs)

    if sub_selected_tab == "SIIC 월간보고":
        st.header("SIIC 월간보고")
        st.write("여기에 SIIC 월간보고에 대한 내용을 작성하세요.")

    elif sub_selected_tab == "SIIC 일간보고":
        st.header("SIIC 일간보고")
        st.write("여기에 SIIC 일간보고에 대한 내용을 작성하세요.")
