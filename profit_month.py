import pandas as pd
import streamlit as st
import plotly.express as px
import openai

openai.api_key = 'sk-proj-3WRQuj4jRabQ7G4YWmr6T3BlbkFJBEtrpdXgUB75VPCzacx0'

def display_profit_page():
    with st.sidebar:
        st.write("hi")
    
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
    gpt_df = profit_df.copy()
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

def gpt(gpt_df):
    gpt_df['날짜'] = pd.to_datetime(gpt_df['날짜'])
    gpt_df['년도'] = gpt_df['날짜'].dt.year
    gpt_df['월'] = gpt_df['날짜'].dt.month
    gpt_df['날짜'] = pd.to_datetime(gpt_df['날짜']).dt.strftime('%Y-%m')
    data_analysis = gpt_df[gpt_df['년도'] == 2024]
    # 데이터프레임에 대한 설명 요청
    prompt = f"n{data_analysis.to_string()} SIIC라는 CS 대행 서비스를 제공하는 업체의 월별 운영실적파일이야. 각 서비스 별로 전월대비 어떠한 변화가 있는지 유의미한 수치 변화가 있는지 분석해줘. 기본적으로 서비스 별로 최근 월이 전월대비 어떠한 변화가 있는지 설명해주고, 각 서비스별로 어떠한 수치적인 변화가 있는지 분석해줘. 또 인사이트가 있다면 제공해줘. "
    response = ask_gpt(prompt)
    return response

# GPT에게 데이터프레임 설명 요청 함수
def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        # max_tokens=1000,
        messages=[
            {"role": "system", "content": "너는 CS 운영실적을 분석하는 컨설턴트야."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']


# GPT 분석 버튼 추가
if st.button('GPT 분석 실행'):
    result = gpt(gpt_df)
    st.session_state['gpt_result'] = result
    # st.write(st.session_state['gpt_result'])

    # GPT 분석 버튼 추가
    if st.button('GPT 분석 실행'):
        st.session_state['gpt_result'] = gpt_analysis(gpt_df)

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
        
        st.write(st.session_state['gpt_result'])
        if 'gpt_result' in st.session_state:
            st.write(st.session_state['gpt_result'])

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

        previous_month = (pd.to_datetime(last_month) - pd.DateOffset(months=1)).strftime("%Y-%m")
        previous_month_data = current_year_data[current_year_data['월'] == previous_month]
        previous_month_revenue = previous_month_data[f'매출:{option}'].sum()
        previous_month_profit = previous_month_data[f'손익:{option}'].sum()

        revenue_delta = last_month_revenue - previous_month_revenue
        profit_delta = last_month_profit - previous_month_profit

        kpis[f'{year}년도 매출누계액'] = current_year_revenue
        kpis[f'{year}년도 손익누계액'] = current_year_profit
        kpis['당월 매출액'] = (last_month_revenue, revenue_delta)
        kpis['당월 손익'] = (last_month_profit, profit_delta)

        return kpis

    def generate_quarterly_charts(data, option, year):
        quarterly_data = data[(data['연도'] == year)].copy()
        
        if f'손익:{option}' not in quarterly_data.columns:
            quarterly_data[f'손익:{option}'] = quarterly_data[f'매출:{option}'] - quarterly_data[f'지출:{option}']

        quarterly_data = quarterly_data.groupby('분기')[[f'매출:{option}', f'손익:{option}']].sum().reset_index()
        
        fig = px.bar(quarterly_data, x='분기', y=[f'매출:{option}', f'손익:{option}'],
                     barmode='group', title=f'{option} 분기별 매출 및 손익',
                     color_discrete_map={
                         f'매출:{option}': 'lightblue',
                         f'손익:{option}': 'red'
                     })
        fig.update_layout(
            yaxis=dict(
                title='금액 (원)',
                tickformat=',.0f',
                tickprefix=""
            ),
            xaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=280  # 분기별 차트 높이 조정
        )
        fig.update_xaxes(tickfont=dict(size=15))
        return fig

    with col2:
        kpis_total = calculate_kpis(profit_df, '전체', selected_total_years[0])
        kpi_keys = list(kpis_total.keys())
        for j in range(0, len(kpi_keys), 2):
            cols = st.columns(2)
            for k, kpi_key in enumerate(kpi_keys[j:j+2]):
                value = kpis_total[kpi_key]
                if isinstance(value, tuple):
                    value, delta = value
                    delta_class = "positive" if delta >= 0 else "negative"
                    delta_text = f"▲ {delta:,}" if delta >= 0 else f"▼ {delta:,}"
                    delta_html = f"<div class='metric-delta {delta_class}'>{delta_text}</div>"
                else:
                    delta_html = ""
                value_class = "negative" if value < 0 else ""
                with cols[k]:
                    st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">{kpi_key}</div>
                            <div class="metric-value {value_class}">{value:,}</div>
                            {delta_html}
                        </div>
                        """, unsafe_allow_html=True)

        fig = generate_quarterly_charts(profit_df, '전체', selected_total_years[0])
        st.plotly_chart(fig)
    '''---'''
    # 세부 항목에 대한 연도 선택
    selected_detail_years = st.multiselect('연도를 선택하세요', years, default=[years[0]])

    # 세부 항목 선택
    options = st.multiselect('서비스를 선택하세요', 
        ['통합상담', 'INC', '스마트팀', '전담상담', '카페24'],
        default=['통합상담', 'INC', '스마트팀', '전담상담', '카페24'])

    # 세부 항목에 대한 데이터 필터링
    filtered_detail_df = profit_df[profit_df['연도'].isin(selected_detail_years)]
    selected_data = calculate_profit(filtered_detail_df, options)

    # 세부 항목 차트 및 데이터프레임 출력
    for i, (option, data) in enumerate(selected_data.items()):
        col1, col2 = st.columns([3, 1])
        with col1:
            data = data.rename(columns={
                f'매출:{option}': '매출',
                f'지출:{option}': '지출',
                f'손익:{option}': '손익'
            })
            
            fig = px.bar(data, x='월', y=['매출', '지출', '손익'],
                         barmode='group', title=f'{option} 매출, 지출, 손익',
                         color_discrete_map={
                             '매출': 'blue',
                             '지출': 'darkblue',
                             '손익': 'red'
                         })
            fig.update_layout(
                yaxis=dict(
                    title='금액 (원)',
                    tickformat=',.0f',
                    tickprefix=""
                ),
                xaxis_title="",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=500  # 차트 높이를 800으로 설정
            )
            fig.update_xaxes(tickformat="%y-%m", tickfont=dict(size=25))
            st.plotly_chart(fig)
            
            with st.expander(f"{option} 데이터 보기"):
                st.dataframe(data)

        with col2:
            kpis = calculate_kpis(profit_df, option, selected_detail_years[0])
            kpi_keys = list(kpis.keys())
            for j in range(0, len(kpi_keys), 2):
                cols = st.columns(2)
                for k, kpi_key in enumerate(kpi_keys[j:j+2]):
                    value = kpis[kpi_key]
                    if isinstance(value, tuple):
                        value, delta = value
                        delta_class = "positive" if delta >= 0 else "negative"
                        delta_text = f"▲ {delta:,}" if delta >= 0 else f"▼ {delta:,}"
                        delta_html = f"<div class='metric-delta {delta_class}'>{delta_text}</div>"
                    else:
                        delta_html = ""
                    value_class = "negative" if value < 0 else ""
                    with cols[k]:
                        st.markdown(f"""
                            <div class="metric-container">
                                <div class="metric-label">{kpi_key}</div>
                                <div class="metric-value {value_class}">{value:,}</div>
                                {delta_html}
                            </div>
                            """, unsafe_allow_html=True)
            
            fig = generate_quarterly_charts(profit_df, option, selected_detail_years[0])
            st.plotly_chart(fig)
            
        '''---'''

# Streamlit 애플리케이션 실행
if __name__ == "__main__":
    display_profit_page()
