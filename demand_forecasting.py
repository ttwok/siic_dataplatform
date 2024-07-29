# demand_forecasting.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import plotly.graph_objects as go
import glob
from datetime import datetime
import os

@st.cache_data
def load_data(folder_path):
    # 현재 파일의 경로를 기준으로 절대 경로 생성
    base_path = os.path.dirname(__file__)
    folder_path = os.path.join(base_path, folder_path)
    csv_files = glob.glob(f'{folder_path}/*.csv')

    def extract_date(file_path):
        file_name = file_path.split('/')[-1]
        date_str = file_name.split('_')[-1].split('.')[0]
        return datetime.strptime(date_str, '%Y-%m')

    latest_file = max(csv_files, key=extract_date)
    df = pd.read_csv(latest_file)
    df = df[['ds', 'y']]
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.set_index('ds')
    df.index.freq = 'MS'
    return df

@st.cache_data
def fit_model(df_log):
    order = (1, 1, 1)
    seasonal_order = (2, 0, 1, 12)
    model = sm.tsa.SARIMAX(df_log, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
    fit_result = model.fit(disp=False, maxiter=1000)
    return fit_result

def call_forecast():
    folder_path = 'data/month_call_total'
    df = load_data(folder_path)

    if not df.empty:
        df_log = np.log(df)

        try:
            predict = fit_model(df_log)
        except Exception as e:
            st.error(f"Model fitting failed: {e}")
            predict = None

        if predict:
            predict_mean = np.exp(predict.get_forecast(7).predicted_mean)
            conf_int = predict.get_forecast(7).conf_int()
            conf_int_lb = np.exp(conf_int['lower y'])
            conf_int_ub = np.exp(conf_int['upper y'])

            fig, ax = plt.subplots(figsize=(14, 5))
            ax.plot(df, color='blue', label='Actual Values')
            ax.plot(predict_mean, label=f'Predicted Values (model = (1,1,1),(2,0,1,12))', color='red', linestyle='--', alpha=0.5)
            ax.fill_between(predict_mean.index, conf_int_lb, conf_int_ub, color='red', alpha=0.1, label='95% Confidence Interval')

            for x, y in zip(df.index, df['y']):
                ax.text(x, y, f'{int(y)}', color='blue', fontsize=8, ha='center', va='bottom')

            for x, y in zip(predict_mean.index, predict_mean):
                ax.text(x, y, f'{int(y)}', color='red', fontsize=8, ha='center', va='bottom')

            ax.set_ylim(20000, 120000)
            ax.legend(loc='upper right')
            ax.set_title('SIIC phone call : total values')
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)

            st.pyplot(fig)

            max_date = df.index.max()
            start_control_date = max_date - pd.DateOffset(months=13)
            min_date = max_date - pd.DateOffset(months=36)
            max_forecast_date = max_date + pd.DateOffset(months=0)

            if 'start_date' not in st.session_state:
                st.session_state.start_date = start_control_date

            start_date = st.slider('control month', min_date.date(), max_forecast_date.date(), value=st.session_state.start_date.date(), format="YYYY-MM")
            st.session_state.start_date = pd.to_datetime(start_date)

            df_filtered = df[st.session_state.start_date:max_date]

            y_min = min(df_filtered['y'].min(), predict_mean.min())
            y_max = max(df_filtered['y'].max(), predict_mean.max())
            y_range_margin = (y_max - y_min) * 0.1

            fig_filtered = go.Figure()

            fig_filtered.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered['y'], mode='lines+markers+text', name='Actual Values',
                                              text=df_filtered['y'].astype(int), textposition='bottom center', textfont=dict(size=10)))

            fig_filtered.add_trace(go.Scatter(x=predict_mean.index, y=predict_mean, mode='lines+markers+text', name='Forcasting Values',
                                              line=dict(dash='dash', color='red'), text=predict_mean.astype(int), textposition='top center', textfont=dict(size=10)))

            fig_filtered.add_trace(go.Scatter(x=predict_mean.index, y=conf_int_lb, fill=None, mode='lines', line_color='red', showlegend=False))
            fig_filtered.add_trace(go.Scatter(x=predict_mean.index, y=conf_int_ub, fill='tonexty', mode='lines', line_color='red', fillcolor='rgba(255, 0, 0, 0.1)', showlegend=False))

            fig_filtered.update_layout(
                title='forcasting M+7',
                yaxis=dict(range=[y_min - y_range_margin, y_max + y_range_margin]),
                xaxis=dict(tickformat='%Y-%m'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                margin=dict(l=40, r=40, t=20, b=40),
                hovermode='x unified',
                height=300
            )

            st.plotly_chart(fig_filtered)
        else:
            st.error("Prediction model fitting failed.")
    else:
        st.error("Failed to retrieve data from Google Sheets.")