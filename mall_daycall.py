# mall_daycall.py
import pandas as pd
import plotly.express as px
import streamlit as st

day_name_map = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}

def load_and_prepare_data(file_path):
    try:
        df_daycall = pd.read_csv(file_path)
        df_daycall = df_daycall[df_daycall['총처리호'] != 0]
        df_daycall['날짜'] = pd.to_datetime(df_daycall['날짜'], format='%Y-%m-%d')
        df_daycall['요일'] = df_daycall['날짜'].dt.weekday.map(day_name_map)
        weekday_order = ['월요일', '화요일', '수요일', '목요일', '금요일']
        df_daycall['요일'] = pd.Categorical(df_daycall['요일'], categories=weekday_order, ordered=True)
        return df_daycall
    except FileNotFoundError:
        st.error(f"File {file_path} not found.")
        return pd.DataFrame()

def plot_daycall_charts(df_daycall):
    if df_daycall.empty:
        st.warning("No data available to plot.")
        return

    df_daycall_daily = df_daycall.groupby(['날짜', '요일'])['총처리호'].sum().reset_index()
    df_daycall_daily = df_daycall_daily[df_daycall_daily['총처리호'] != 0]
    df_daycall_daily = df_daycall_daily.sort_values(by='날짜')

    # 전체 콜 현황
    df_daycall['월'] = df_daycall['날짜'].dt.to_period('M')
    df_month_call = df_daycall.groupby('월')['총처리호'].sum().reset_index()
    df_month_call['월'] = df_month_call['월'].astype(str)
    df_month_call = df_month_call.sort_values(by='월', ascending=False)

    fig3 = px.bar(df_month_call, x='월', y='총처리호', title='월별 총 콜 처리현황')
    st.plotly_chart(fig3, use_container_width=True)

    fig2 = px.bar(df_daycall_daily, x='날짜', y='총처리호', title='일자별 총 콜 처리현황')
    st.plotly_chart(fig2, use_container_width=True)

    fig = px.line(df_daycall_daily, x='날짜', y='총처리호', color='요일', title='요일별 콜 처리현황')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

def display_team_data(df_daycall, team_name):
    selected_teams = st.multiselect('조회 대상 부서를 선택하세요', [*team_name])
    df_selected_teams = df_daycall[df_daycall['팀명'].isin(selected_teams)]

    t1, t2 = st.tabs(['월별', '일자별'])

    with t1:
        df_selected_teams['월'] = df_selected_teams['날짜'].dt.to_period('M')
        df_monthly = df_selected_teams.groupby(['월', '팀명'])['총처리호'].sum().reset_index()
        df_monthly['월'] = df_monthly['월'].astype(str)

        df_pivot_monthly = df_monthly.pivot_table(index='월', columns='팀명', values='총처리호', aggfunc='sum').reset_index()
        df_melted_monthly = df_pivot_monthly.melt(id_vars='월', value_vars=df_pivot_monthly.columns[1:], var_name='부서', value_name='처리호')
        df_melted_monthly = df_melted_monthly.dropna()

        fig_bar_monthly = px.bar(df_melted_monthly, x='월', y='처리호', color='부서', barmode='group', title='월별 부서별 콜 처리현황')
        fig_bar_monthly.update_layout(yaxis_title='처리호', xaxis_title='월', xaxis={'categoryorder': 'category ascending'}, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar_monthly, use_container_width=True)

        fig_stack_bar_monthly = px.bar(df_melted_monthly, x='월', y='처리호', color='부서', barmode='stack', title='월별 부서별 콜 처리현황 (누적)')
        fig_stack_bar_monthly.update_layout(yaxis_title='처리호', xaxis_title='월', xaxis={'categoryorder': 'category ascending'}, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_stack_bar_monthly, use_container_width=True)

        st.write('*raw data*')
        st.dataframe(df_pivot_monthly)

    with t2:
        last_date = df_selected_teams['날짜'].max()
        start_date = last_date - pd.Timedelta(days=10)
        df_filtered = df_selected_teams[(df_selected_teams['날짜'] >= start_date) & (df_selected_teams['날짜'] <= last_date)]

        df_pivot = df_filtered.pivot_table(index='날짜', columns='팀명', values='총처리호', aggfunc='sum').reset_index()
        df_pivot = df_pivot.sort_values(by='날짜', ascending=False)

        df_melted = df_pivot.melt(id_vars='날짜', value_vars=df_pivot.columns[1:], var_name='부서', value_name='처리호')
        df_melted = df_melted.dropna()

        fig_bar = px.bar(df_melted, x='날짜', y='처리호', color='부서', barmode='group', title='일자별 부서별 콜 처리현황')
        fig_bar.update_layout(yaxis_title='처리호', xaxis_title='날짜', xaxis={'categoryorder':'category ascending'}, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_area = px.area(df_melted, x='날짜', y='처리호', color='부서', title='일자별 부서별 콜 처리 현황 (영역형)')
        fig_area.update_layout(yaxis_title='처리호', xaxis_title='날짜', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_area, use_container_width=True)

        st.write('*raw data*')
        st.dataframe(df_pivot)

def display_mall_data(df_daycall, mall_name):
    selected_malls = st.multiselect('업체를 선택하세요', [*mall_name])
    df_selected_malls = df_daycall[df_daycall['쇼핑몰명'].isin(selected_malls)]

    df_selected_malls['월'] = df_selected_malls['날짜'].dt.to_period('M')
    df_monthly_mall = df_selected_malls.groupby(['월', '쇼핑몰명'])['총처리호'].sum().reset_index()
    df_monthly_mall['월'] = df_monthly_mall['월'].astype(str)

    fig_mall_monthly = px.line(df_monthly_mall, x='월', y='총처리호', color='쇼핑몰명', title='월별 업체별 콜 처리 추이')
    fig_mall_monthly.update_layout(yaxis_title='처리호', xaxis_title='월', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_mall_monthly, use_container_width=True)

    last_date_mall = df_selected_malls['날짜'].max()
    start_date_mall = last_date_mall - pd.Timedelta(days=90)
    df_daily_mall = df_selected_malls[(df_selected_malls['날짜'] >= start_date_mall) & (df_selected_malls['날짜'] <= last_date_mall)]

    fig_mall_daily = px.area(df_daily_mall, x='날짜', y='총처리호', color='쇼핑몰명', title='일별 업체별 콜 처리 현황 (90일)')
    fig_mall_daily.update_layout(yaxis_title='처리호', xaxis_title='날짜', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_mall_daily, use_container_width=True)

    st.write('*raw data (월별)*')
    st.dataframe(df_monthly_mall)

    st.write('*raw data (일별)*')
    st.dataframe(df_daily_mall[['날짜','쇼핑몰명','총처리호']])
