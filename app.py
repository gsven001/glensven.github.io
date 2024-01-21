from pathlib import Path
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

# Load Cook County Covid Mortality Data
csv_file_path = Path("assets/pds.csv")
df_covid = pd.read_csv(csv_file_path)

# Convert the Index 'Date of Death' to datetime
df_covid['DATE_OF_DEATH'] = pd.to_datetime(df_covid['DATE_OF_DEATH'])
df_covid.set_index('DATE_OF_DEATH', inplace=True)

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

morbidity_list = list(df_covid['MORBIDITY'].unique())

morbidity_value = 'No Filtering'

morbidity_list.append(morbidity_value)
#---------------------------------------------------------------------------------------
# Create the layout of the app
app.layout = html.Div([
    #TASK 2.1 Add title to the dashboard
    html.H1("Covid-Related Deaths, Cook County, IL Dashboard", style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),#May include style for title
    html.Div([#TASK 2.2: Add two dropdown menus
        html.Label("Select Rolling Window:"),
        dcc.Dropdown(
            id='trend-statistics',
            options=trend_options,
            value= 1,
            placeholder='Select Rolling Window',
            style={'textAlign': 'center', 'font-size': 20, 'padding': 3, 'width': 400}
        ),html.Br(),
        html.P("Select Morbidity"),
        dcc.Dropdown(
            id="morbidity-select",
            options=[{"label": i, "value": i} for i in morbidity_list],
            value=morbidity_list[:],
            placeholder="All Morbidities Selected",
            searchable= True,
            clearable= True,
            multi=True,
            maxHeight=500
        ),
    ]),
    html.Div([#TASK 2.3: Add a division for output display
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})])
])
#TASK 2.4: Creating Callbacks
# Define the callback function to update the input container based on the selected statistics

# @app.callback(
#     Output('morbidity-select', 'value'),
#     Input('morbidity-select', 'options'),
#     Input('morbidity-select', 'value')
# )
# def update_dropdown_value(options, selected_values):
#     # Check if no options are selected or if selected values are not in the current options
#     if not selected_values or any(val not in [option['value'] for option in options] for val in selected_values):
#         # Return the original value
#         return morbidity_value
#     else:
#         # Return the selected values
#         return selected_values

@app.callback(
    Output(component_id='output-container', component_property='children'),
    Input(component_id='trend-statistics',component_property='value'),
    Input(component_id='morbidity-select',component_property='value'))
def rolling_trends(time_span, morbidity):
    # Count distinct CASE_NUMBER by Day, 7 days, 30 days

    if morbidity == 'No Filtering':
        df_covid_trend_filtered = df_covid.reset_index()
    else:
        df_covid_trend_filtered = df_covid[df_covid['MORBIDITY'].isin(morbidity)].reset_index()

    if time_span == 1:
        df_covid_trend_daily = df_covid_trend_filtered.groupby(df_covid_trend_filtered['DATE_OF_DEATH'])['CASE_NUMBER'].nunique().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(df_covid_trend_daily,
                           x='DATE_OF_DEATH',
                           y='CASE_NUMBER',
                           labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                           title="Daily Total Deaths"))
    elif time_span == 7:
        df_covid_trend_weekly = df_covid_trend_filtered.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(window=7).sum().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(df_covid_trend_weekly,
                           x='DATE_OF_DEATH',
                           y='CASE_NUMBER',
                           labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                           title="7 Day Rolling Average of Total Deaths"))
    else:
        df_covid_trend_monthly = df_covid_trend_filtered.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(window=30).sum().reset_index()

        R_chart1 = dcc.Graph(
            figure=px.line(df_covid_trend_monthly,
                           x='DATE_OF_DEATH',
                           y='CASE_NUMBER',
                           labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                           title="30 Day Rolling Average of Total Deaths"))

    print(df_covid['MORBIDITY'].unique())
    return [
        html.Div(className='chart-item', children=[html.Div(children=R_chart1)]),
        # html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
    ]

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)