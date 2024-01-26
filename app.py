from pathlib import Path
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from collections import Counter
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime as dt

# Load Cook County Covid Mortality Data
csv_file_path = Path("assets/pds_final.csv")
css_file_path = Path("css/style.css")
df_covid = pd.read_csv(csv_file_path, dtype={19: str, 20: str})

# Convert the Index 'Date of Death' to datetime
df_covid['DATE_OF_DEATH'] = pd.to_datetime(df_covid['DATE_OF_DEATH'], errors='coerce').dt.date

# Convert Age and Total Morbidities to Integer
df_covid['AGE'] = pd.to_numeric(df_covid['AGE'], errors='coerce').astype('Int64')
df_covid['TOTAL_MORBIDITIES'] = pd.to_numeric(df_covid['TOTAL_MORBIDITIES'], errors='coerce').astype('Int64')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Covid-Related Deaths, Cook County, IL Dashboard"

#---------------------------------------------------------------------------------
# Create the dropdown menu options
trend_options = [
    {'label': 'Daily', 'value': 1},
    {'label': '7 Day', 'value': 7},
    {'label': '30 Day', 'value': 30}
]

# Drop Covid-19 from the list
df_no_covid = df_covid[df_covid['GENERAL_MORBIDITY'] != 'COVID-19']

morbidity_list = list(df_no_covid['GENERAL_MORBIDITY'])

morbidity_counts = Counter(morbidity_list)

# Extract unique values and count occurrences
unique_values_counts = df_no_covid['GENERAL_MORBIDITY'].value_counts()

# Sort unique values by count (most occurrences to least)
sorted_unique_values_counts = unique_values_counts.sort_values(ascending=False)

# Create a list of tuples with (value, count)
sorted_unique_values_and_counts = [(value, count) for value, count in zip(sorted_unique_values_counts.index, sorted_unique_values_counts)]

# Print the list of tuples
# print(sorted_unique_values_and_counts)

strings_list = [f"{value}" for value, count in zip(sorted_unique_values_counts.index, sorted_unique_values_counts)]

# Calculate the sum of counts for each unique value

sorted_morbidity_list = sorted(morbidity_counts.keys(), key=lambda x: morbidity_counts[x], reverse=True)

# Sort options by the sum of counts (descending order)



#---------------------------------------------------------------------------------------
# Layout of the app
app.layout = html.Div([
    html.Div([
        html.Link(
            rel='stylesheet',
            href=css_file_path
        ),
        html.Div(
                [
            html.Div(
                id="left-column",
                children=[

            html.H1("Covid-Related Deaths, Cook County, IL Dashboard",
                    style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}),
            html.Br(),
            html.Label("Select Rolling Window:"),
            dcc.Dropdown(
                id='trend-statistics',
                options=trend_options,
                value=7,
                placeholder='Select Rolling Window',
                clearable=False,
                style={'textAlign': 'center', 'font-size': 20, 'padding': 3, 'width': 400}
            ),
            html.P("Select a Date Range:"),
            dcc.DatePickerRange(
                id='date-slider',
                start_date=df_covid['DATE_OF_DEATH'].min(),
                end_date=df_covid['DATE_OF_DEATH'].max(),
                display_format='YYYY-MM-DD',
                style={'textAlign': 'center', 'font-size': 20, 'padding': 3, 'width': 400}
            ),
            html.P("Select General Morbidity Category"),
            dcc.Dropdown(
                id="morbidity-select",
                options=sorted_morbidity_list,
                value=sorted_morbidity_list[:5],
                placeholder="No General Morbidity Selected",
                searchable=True,
                clearable=True,
                multi=True,
                maxHeight=300,
                # disabled=True,
                style={'textAlign': 'center', 'font-size': 20, 'padding': 5, 'width': 400}
            ),
        ], className='app-controls'),
        html.Div(
            id="right-column",
            children=[html.Div(id='output-container', style={'display': 'flex'})],
            className='app-graphs')
    ], className='app-container')
    ])
    ])
@app.callback(
    [Output(component_id='output-container', component_property='children')],
    [Input(component_id='morbidity-select', component_property='value'),
     Input(component_id='trend-statistics', component_property='value'),
     Input(component_id='date-slider', component_property='start_date'),
     Input(component_id='date-slider', component_property='end_date')])

def rolling_trends(morbidity, time_span, start_date, end_date):

    # Filter data based on selected date range
    filtered_by_date = df_covid[(pd.to_datetime(df_covid['DATE_OF_DEATH']) >= pd.to_datetime(start_date)) & (pd.to_datetime(df_covid['DATE_OF_DEATH']) <= pd.to_datetime(end_date))]

    if morbidity is not None:
        fig = make_subplots(rows=1, cols=1, subplot_titles=(""))
        if time_span == 1:
            # df_filtered = filtered_by_date[filtered_by_date['GENERAL_MORBIDITY'].isin(morbidity)]
            df_covid_trend_daily = filtered_by_date.groupby(['DATE_OF_DEATH', 'GENERAL_MORBIDITY'])['CASE_NUMBER'].nunique().reset_index()
            df_covid_trend_daily['CASE_NUMBER'] = df_covid_trend_daily['CASE_NUMBER'].fillna(0)
            fig.update_xaxes(title_text='Date of Death')
            fig.update_yaxes(title_text='Deaths')
            fig.update_layout(title_text="Daily Total Deaths")
            for morbid in morbidity:
                morbid_data = df_covid_trend_daily[df_covid_trend_daily['GENERAL_MORBIDITY'] == morbid]
                trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'], mode='lines', name=morbid)
                fig.add_trace(trace)

        elif time_span == 7:
            # df_filtered = filtered_by_date[filtered_by_date['GENERAL_MORBIDITY'].isin(morbidity)]
            df_covid_trend_weekly = filtered_by_date.groupby(['DATE_OF_DEATH', 'GENERAL_MORBIDITY'])['CASE_NUMBER'].nunique().reset_index()
            df_covid_trend_weekly['CASE_NUMBER'] = df_covid_trend_weekly.groupby('GENERAL_MORBIDITY')['CASE_NUMBER'].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
            df_covid_trend_weekly['CASE_NUMBER'] = df_covid_trend_weekly['CASE_NUMBER'].fillna(0)
            fig.update_xaxes(title_text='Date of Death')
            fig.update_yaxes(title_text='Deaths')
            fig.update_layout(title_text="7 Day Rolling Average of Total Deaths")
            for morbid in morbidity:
                morbid_data = df_covid_trend_weekly[df_covid_trend_weekly['GENERAL_MORBIDITY'] == morbid]
                trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'], mode='lines', name=morbid)
                fig.add_trace(trace)
        else:
            # df_filtered = filtered_by_date[filtered_by_date['GENERAL_MORBIDITY'].isin(morbidity)]
            df_covid_trend_monthly = filtered_by_date.groupby(['DATE_OF_DEATH', 'GENERAL_MORBIDITY'])['CASE_NUMBER'].nunique().reset_index()
            df_covid_trend_monthly['CASE_NUMBER'] = df_covid_trend_monthly.groupby('GENERAL_MORBIDITY')['CASE_NUMBER'].rolling(window=30, min_periods=1).mean().reset_index(level=0, drop=True)
            df_filtered['CASE_NUMBER'] = df_filtered['CASE_NUMBER'].fillna(0)
            fig.update_xaxes(title_text='Date of Death')
            fig.update_yaxes(title_text='Deaths')
            fig.update_layout(title_text="30 Day Rolling Average of Total Deaths")
            for morbid in morbidity:
                morbid_data = df_covid_trend_monthly[df_covid_trend_monthly['GENERAL_MORBIDITY'] == morbid]
                trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'], mode='lines', name=morbid)
                fig.add_trace(trace)
        legend_size = len(trace.name) * 10
        fig.update_layout(width=1000 + legend_size, height=600)
        fig.update_layout(legend=dict(x=1, y=1, xanchor='left', yanchor='top', traceorder='normal'))
    else:
        fig = make_subplots(rows=1, cols=1, subplot_titles=(""))
        if time_span == 1:
            df_covid_trend_daily = filtered_by_date.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().reset_index()
            fig.update_xaxes(title_text='Date of Death')
            fig.update_yaxes(title_text='Deaths')
            fig.update_layout(title_text="Daily Total Deaths")
            fig.add_trace(go.Scatter(x=df_covid_trend_daily['DATE_OF_DEATH'], y=df_covid_trend_daily['CASE_NUMBER'], mode='lines'))
        elif time_span == 7:
            df_covid_trend_weekly = filtered_by_date.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(
                window=7).mean().reset_index()
            fig.update_xaxes(title_text='Date of Death')
            fig.update_yaxes(title_text='Deaths')
            fig.update_layout(title_text="7 Day Rolling Average of Total Deaths")
            fig.add_trace(go.Scatter(x=df_covid_trend_weekly['DATE_OF_DEATH'], y=df_covid_trend_weekly['CASE_NUMBER'], mode='lines'))
        else:
            df_covid_trend_monthly = filtered_by_date.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(
                window=30).mean().reset_index()
            fig.update_xaxes(title_text='Date of Death')
            fig.update_yaxes(title_text='Deaths')
            fig.update_layout(title_text="30 Day Rolling Average of Total Deaths")
            fig.add_trace(go.Scatter(x=df_covid_trend_monthly['DATE_OF_DEATH'], y=df_covid_trend_monthly['CASE_NUMBER'], mode='lines'))
        fig.update_layout(width=800, height=600)
    return [dcc.Graph(figure=fig)]
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)