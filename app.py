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

# Load Cook County Covid Mortality Data
csv_file_path = Path("assets/pds.csv")
df_covid = pd.read_csv(csv_file_path)

# Convert the Index 'Date of Death' to datetime
df_covid['DATE_OF_DEATH'] = pd.to_datetime(df_covid['DATE_OF_DEATH']).dt.date

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

morbidity_list = list(df_covid['MORBIDITY'])

morbidity_counts = Counter(morbidity_list)

# Drop Covid-19 from the list
df_no_covid = df_covid[df_covid['MORBIDITY'] != 'COVID-19']

# Extract unique values and count occurrences
unique_values_counts = df_no_covid['MORBIDITY'].value_counts()

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
# Create the layout of the app
app.layout = html.Div([
    #TASK 2.1 Add title to the dashboard
    html.H1("Covid-Related Deaths, Cook County, IL Dashboard", style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),#May include style for title
    html.Div([#TASK 2.2: Add two dropdown menus
        html.Label("Select Rolling Window:"),
        dcc.Dropdown(
            id='trend-statistics',
            options=trend_options,
            value=7,
            placeholder='Select Rolling Window',
            clearable= False,
            style={'textAlign': 'center', 'font-size': 20, 'padding': 3, 'width': 400}
        ),
        html.P("Filter by Morbidity:"),
        dcc.RadioItems(
        id='radio-item',
        options=[
            {'label': 'No Filter', 'value': 'disable'},
            {'label': 'Filter', 'value': 'enable'}
        ],
        value='disable'),
        html.Br(),
        html.P("Select Co-Morbidities"),
        dcc.Dropdown(
            id="morbidity-select",
            options=strings_list,
            value=[strings_list[0]],
            placeholder="No Morbidity Selected",
            searchable= True,
            clearable= True,
            multi=True,
            maxHeight=500,
            disabled=True,
            style={'textAlign': 'center', 'font-size': 20, 'padding': 3, 'width': 900}
        ),
    ]),
    html.Div([#TASK 2.3: Add a division for output display
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})])
])

@app.callback(
    [Output('morbidity-select', 'options'),
     Output('morbidity-select', 'disabled')],
    [Input('radio-item', 'value')]
)
def update_dropdown_options(selected_radio):
    if selected_radio == 'enable':
        options = strings_list
        disabled = False  # Enable the dropdown
    else:
        options = []  # Empty options when disabled
        disabled = True  # Disable the dropdown

    return options, disabled


@app.callback(
    [Output(component_id='output-container', component_property='children')],
    [Input(component_id='morbidity-select',component_property='value'),
    Input(component_id='radio-item',component_property='value'),
    Input(component_id='trend-statistics',component_property='value')])

def rolling_trends(morbidity, selected_radio, time_span):
    # Count distinct CASE_NUMBER by Day, 7 days, 30 days

    if selected_radio == 'disable':
        df_covid_trend_filtered = df_covid
        if time_span == 1:
            df_covid_trend_daily = df_covid_trend_filtered.groupby(df_covid_trend_filtered['DATE_OF_DEATH'])[
                'CASE_NUMBER'].nunique().reset_index()
            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_daily,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="Daily Total Deaths"))
        elif time_span == 7:
            df_covid_trend_weekly = df_covid_trend_filtered.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(
                window=7).mean().reset_index()
            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_weekly,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="7 Day Rolling Average of Total Deaths"))
        else:
            df_covid_trend_monthly = df_covid_trend_filtered.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(
                window=30).mean().reset_index()

            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_monthly,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="30 Day Rolling Average of Total Deaths"))
    elif selected_radio == 'enable' and morbidity is not None:
        df_covid_trend_filtered = df_covid[df_covid['MORBIDITY'].isin(morbidity)]
        if time_span == 1:
            df_covid_trend_daily = df_covid_trend_filtered.groupby(df_covid_trend_filtered['DATE_OF_DEATH'])[
                'CASE_NUMBER'].nunique().reset_index()
            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_daily,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="Daily Total Deaths"))
        elif time_span == 7:
            df_covid_trend_weekly = df_covid_trend_filtered.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(
                window=7).mean().reset_index()
            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_weekly,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="7 Day Rolling Average of Total Deaths"))
        else:
            df_covid_trend_monthly = df_covid_trend_filtered.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(
                window=30).mean().reset_index()

            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_monthly,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="30 Day Rolling Average of Total Deaths"))
    else:

        if time_span == 1:
            df_covid_trend_daily = df_covid.groupby(df_covid['DATE_OF_DEATH'])['CASE_NUMBER'].nunique().reset_index()
            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_daily,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="Daily Total Deaths"))
        elif time_span == 7:
            df_covid_trend_weekly = df_covid.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(window=7).mean().reset_index()
            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_weekly,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="7 Day Rolling Average of Total Deaths"))
        else:
            df_covid_trend_monthly = df_covid.groupby('DATE_OF_DEATH')['CASE_NUMBER'].nunique().rolling(window=30).mean().reset_index()

            R_chart1 = dcc.Graph(
                figure=px.line(df_covid_trend_monthly,
                               x='DATE_OF_DEATH',
                               y='CASE_NUMBER',
                               labels={'DATE_OF_DEATH': 'Date of Death', 'CASE_NUMBER': 'Deaths'},
                               title="30 Day Rolling Average of Total Deaths"))


    return [
        html.Div(className='chart-item', children=[html.Div(children=R_chart1)]),
        # html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
    ]

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)