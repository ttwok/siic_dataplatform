import pandas as pd
import streamlit as st
import plotly.express as px

def display_profit_page():
    # CSS 스타일 추가
    st.markdown("""
        <style>
        .metric-container {
            padding: 10px;
            margin: 5px;
            text-align: right;
        }
        .metric-label {
            font-size: 20px;
        }
        .metric-value {
            font-size: 25px;
            font-weight: bold;
        }
        .metric-value.negative {
            color: red;
        }
        .metric-delta {
            font-size: 15px;
        }
        .metric-delta.positive {
            color: green;
        }
        .metric-delta.negative {
            color: red;
        }
        </style>
        """, unsafe_allow_html=True)

    # 데이터 불러오기
    profit_df = pd.read_excel('data/profit_month/profit_month.xlsx')
    profit_df['날짜'] = pd.to_datetime(profit_df['날짜'])
    profit_df['연도'] = profit_df['날짜'].dt.year
    profit_df['월'] = profit_df['날짜'].dt.strftime("%Y-%m")
    profit_df['분기'] = profit_df['날짜'].dt.to_period('Q').astype(str)

    # 전체 매출, 지출, 손익 계산
    profit_df['매출:전체'] = profit_df[[col for col in profit_df.columns if col.startswith('매출:')]].sum(axis=1)
    profit_df['지출:전체'] = profit_df[[col for col in profit_df.columns if col.startswith('지출:')]].sum(axis=1)
    profit_df['손익:전체'] = profit_df['매출:전체'] - profit_df['지출:전체']

    # 선택한 항목에 따른 매출, 지출, 손익 계산
    def calculate_profit(df, options):
        result = {}
        for option in options:
            revenue_col = f'매출:{option}'
            expense_col = f'지출:{option}'
            
            if revenue_col in df.columns and expense_col in df.columns:
                df = df.copy()
                df[f'손익:{option}'] = df[revenue_col] - df[expense_col]
                result[option] = df[['월', revenue_col, expense_col, f'손익:{option}']]
        return result

    # 전체 매출에 대한 연도 선택
    years = sorted(profit_df['연도'].unique(), reverse=True)
    selected_total_years = st.multiselect('전체 매출 연도를 선택하세요', years, default=[years[0]])

    # 전체 매출, 지출, 손익을 연도별로 필터링하여 시각화
    filtered_total_df = profit_df[profit_df['연도'].isin(selected_total_years)]
    total_data = filtered_total_df[['월', '매출:전체', '지출:전체', '손익:전체']]

    # 전체 차트 출력
    col1, col2 = st.columns([3, 1])
    with col1:
        fig_total = px.bar(total_data, x='월', y=['매출:전체', '지출:전체', '손익:전체'],
                           barmode='group', title='전체 매출, 지출, 손익',
                           color_discrete_map={
                               '매출:전체': 'blue',
                               '지출:전체': 'darkblue',
                               '손익:전체': 'red'
                           })
        fig_total.update_layout(
            yaxis=dict(
                title='금액 (원)',
                tickformat=',.0f',  # y축 단위 포맷 설정
                tickprefix=""
            ),
            xaxis_title="",  # x축 제목 제거
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=550  # 차트 높이를 800으로 설정
        )
        fig_total.update_xaxes(tickformat="%y-%m", tickfont=dict(size=25))  # x축 글자 크기 변경
        st.plotly_chart(fig_total, use_container_width=True)

        with st.expander("전체 데이터 보기"):
            st.dataframe(total_data)

    def calculate_kpis(data, option, year):
        kpis = {}
        current_year_data = data[(data['연도'] == year)].copy()
        
        # 손익 계산 보정
        if f'손익:{option}' not in current_year_data.columns:
            current_year_data[f'손익:{option}'] = current_year_data[f'매출:{option}'] - current_year_data[f'지출:{option}']
        
        current_year_revenue = current_year_data[f'매출:{option}'].sum()
        current_year_profit = current_year_data[f'손익:{option}'].sum()

        last_month = current_year_data['월'].max()
        last_month_data = current_year_data[current_year_data['월'] == last_month]
        last_month_revenue = last_month_data[f'매출:{option}'].sum()
        last_month_profit = last_month_data[f'손익:{option}'].sum()

        previous_month = (pd.to_datetime(last_month) -
