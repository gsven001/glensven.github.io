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
file_path = Path("assets/final_data.csv")


def load_data(file_path):
    #Read csv
    df = pd.read_csv(file_path, dtype={6: str})
    # Convert the Index 'Date of Death' to datetime
    df['DATE_OF_DEATH'] = pd.to_datetime(df['DATE_OF_DEATH'], errors='coerce').dt.date
    # Convert Age and Total Morbidities to Integer
    df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce').astype('Int64')
    df['TOTAL_MORBIDITIES'] = pd.to_numeric(df['TOTAL_MORBIDITIES'], errors='coerce').astype('Int64')
    # Shorten CANCER label
    df['GENERAL_MORBIDITY'] = df['GENERAL_MORBIDITY'].replace('CANCER: LEUKEMIA, MALIGNANT TUMOR, LYMPHOMA, ETC.', 'CANCER')
    # Convert NA's to numeric
    pd.to_numeric(df['AGE'], errors='coerce').astype('Int64')
    # Remove Covid-19 label as it is unnecessary
    df_no_covid = df[df['GENERAL_MORBIDITY'] != 'COVID-19']
    return df, df_no_covid


df_covid, df_no_covid = load_data(file_path)

# Create list of Morbidities
morbidity_list = list(df_no_covid['GENERAL_MORBIDITY'])

# Count the frequency of the morbidities
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

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=["assets/css/style.css"])

# Set the title of the dashboard
app.title = "Covid-Related Deaths, Cook County, IL Dashboard"

#---------------------------------------------------------------------------------
# Create the dropdown menu options
trend_options = [
    {'label': 'Daily', 'value': 1},
    {'label': '7 Day', 'value': 7},
    {'label': '30 Day', 'value': 30}
]
#---------------------------------------------------------------------------------------
# Layout of the app
app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href="assets/css/style.css"
    ),
    html.Div([
        html.Div(
            id="app-controls",
            children=[
                html.Div([html.H1("Covid-Related Deaths Dashboard",
                        style={'textAlign': 'center', 'color': '#ffffff', 'fontSize': 30}),
                html.H1("Cook County, IL",
                        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 22}),
                ]),
                html.Br(),
                html.Label("Select Rolling Window:"),
                dcc.Dropdown(
                    id='trend-statistics',
                    options=trend_options,
                    value=30,
                    placeholder='Select Rolling Window',
                    clearable=False,
                    style={'textAlign': 'center', 'fontSize': 20, 'padding': 3, 'width': 400}
                ),
                html.P("Select a Date Range:"),
                dcc.DatePickerRange(
                    id='date-slider',
                    start_date=df_covid['DATE_OF_DEATH'].min(),
                    end_date=dt(2022, 7, 1),
                    display_format='YYYY-MM-DD',
                    style={'textAlign': 'center', 'fontSize': 20, 'padding': 3, 'width': 400}
                ),
                html.P("Select a Sex:"),
                dcc.Checklist(
                    id='sex-select',
                    options=[
                        {
                            "label": html.Div(['Female'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "Female"
                        },
                        {
                            "label": html.Div(['Male'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "Male"
                        },
                        ],
                    value=['Female', 'Male'],
                    labelStyle={"display": "flex", "align-items": "right"},
                    inline=True
                ),
                html.P("Select a Race:"),
                dcc.Checklist(
                    id='race-select',
                    options=[
                        {
                            "label": html.Div(['White'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "White"
                        },
                        {
                            "label": html.Div(['Black'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "Black"
                        },
                        {
                            "label": html.Div(['Asian'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "Asian"
                        },
                        {
                            "label": html.Div(['Other'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "Other"
                        },
                        {
                            "label": html.Div(['Am. Indian'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "Am. Indian"
                        },
                        {
                            "label": html.Div(['Unknown'], style={'color': '#dff4f5', 'fontSize': 20}),
                            "value": "Unknown"
                        }
                    ],
                    value=['White', 'Black', 'Asian', 'Other', 'Am. Indian', 'Unknown'],
                    labelStyle={"display": "flex", "align-items": "right"},
                ),
                html.P("Select an Age Range:"),
                dcc.RangeSlider(
                    min=0,
                    max=120,
                    step=10,
                    value=(0, 120),
                    allowCross=False,
                    id='age-slider',
                    tooltip={"placement": "bottom", "always_visible": True},
                    marks={str(h): {'label': str(h), 'style': {'color': '#dff4f5'}} for h in range(0, 121, 10)}
                ),
                html.P("Select General Morbidity Category"),
                dcc.Dropdown(
                    id="morbidity-select",
                    options=[{'label': value, 'value': value} for value in sorted_morbidity_list],
                    value=sorted_morbidity_list[:1],
                    placeholder="No General Morbidity Selected",
                    searchable=True,
                    clearable=False,
                    multi=True,
                    maxHeight=300,
                    style={'textAlign': 'center', 'fontSize': 20, 'padding': 5, 'width': 400}
                ),
            ],
            className='app-controls'
        ),
        html.Div(
            id="app-graphs",
            children=[html.Div(id='output-container')],
            className='app-graphs'

        ),
    ], style={'display': 'flex', 'height': '100vh', 'width': '100vw'})
], style={'display': 'flex', 'height': '100vh', 'width': '100vw'})


@app.callback(
    [Output(component_id='output-container', component_property='children')],
    [Input(component_id='morbidity-select', component_property='value'),
     Input(component_id='trend-statistics', component_property='value'),
     Input(component_id='date-slider', component_property='start_date'),
     Input(component_id='date-slider', component_property='end_date'),
     Input(component_id='age-slider', component_property='value'),
     Input(component_id='sex-select', component_property='value'),
     Input(component_id='race-select', component_property='value')])

def rolling_trends(morbidity, time_span, start_date, end_date, age, sex, race):

    # Filter data based on selected date range
    filtered_df = df_no_covid[(pd.to_datetime(df_no_covid['DATE_OF_DEATH']) >= pd.to_datetime(start_date)) & (pd.to_datetime(df_no_covid['DATE_OF_DEATH']) <= pd.to_datetime(end_date))]
    # Filter data based on selected age range
    filtered_df = filtered_df[filtered_df['AGE'].between(age[0], age[1])]
    # Filter by sex
    filtered_df['GENDER'] = filtered_df['GENDER'].fillna('Unknown')
    filtered_df = filtered_df[filtered_df['GENDER'].isin(sex)]
    # Filter_by_race
    filtered_df['RACE'] = filtered_df['RACE'].fillna('Unknown')
    filtered_df = filtered_df[filtered_df['RACE'].isin(race)]
    filtered_data = filtered_df.groupby(['DATE_OF_DEATH', 'GENERAL_MORBIDITY'])['CASE_NUMBER'].nunique().reset_index()

    fig = make_subplots(rows=1, cols=1, subplot_titles=(""))
    if time_span == 1:
        fig.update_layout(title_text=f"Daily Total Deaths Between Ages {age[0]} and {age[1]}")
        for morbid in morbidity:
            morbid_data = filtered_data[filtered_data['GENERAL_MORBIDITY'] == morbid]
            trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'], mode='lines', name=morbid)
            fig.add_trace(trace)
    elif time_span == 7:
        # df_filtered = filtered_by_date[filtered_by_date['GENERAL_MORBIDITY'].isin(morbidity)]
        df_covid_trend_weekly = filtered_data.copy()
        df_covid_trend_weekly['CASE_NUMBER'] = df_covid_trend_weekly.groupby('GENERAL_MORBIDITY')['CASE_NUMBER'].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df_covid_trend_weekly['CASE_NUMBER'] = df_covid_trend_weekly['CASE_NUMBER'].fillna(0)
        fig.update_layout(title_text=f"7 Day Rolling Average of Total Deaths Between Ages {age[0]} and {age[1]}")
        for morbid in morbidity:
            morbid_data = df_covid_trend_weekly[df_covid_trend_weekly['GENERAL_MORBIDITY'] == morbid]
            trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'], mode='lines', name=morbid)
            fig.add_trace(trace)
    else:
        # df_filtered = filtered_by_date[filtered_by_date['GENERAL_MORBIDITY'].isin(morbidity)]
        df_covid_trend_monthly = filtered_data.copy()
        df_covid_trend_monthly['CASE_NUMBER'] = df_covid_trend_monthly.groupby('GENERAL_MORBIDITY')['CASE_NUMBER'].rolling(window=30, min_periods=1).mean().reset_index(level=0, drop=True)
        df_covid_trend_monthly['CASE_NUMBER'] = df_covid_trend_monthly['CASE_NUMBER'].fillna(0)
        fig.update_layout(title_text=f"30 Day Rolling Average of Total Deaths Between Ages {age[0]} and {age[1]}")
        for morbid in morbidity:
            morbid_data = df_covid_trend_monthly[df_covid_trend_monthly['GENERAL_MORBIDITY'] == morbid]
            trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'], mode='lines', name=morbid)
            fig.add_trace(trace)
    fig.update_xaxes(title_text='Date of Death')
    fig.update_yaxes(title_text='Deaths')
    fig.update_layout(showlegend=True)
    fig.update_layout(width=1000, height=600)
    fig.update_layout(legend=dict(x=1, y=1, xanchor='left', yanchor='top', traceorder='normal'))

    return [dcc.Graph(figure=fig)]
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)