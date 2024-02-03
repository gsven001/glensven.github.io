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

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=["assets/css/style.css"])

server = app.server
app.config.suppress_callback_exceptions = True

# Set the title of the dashboard
app.title = "Covid-Related Deaths, Cook County, IL Dashboard"

# Load Cook County Covid Mortality Data
file_path = Path("assets/real_cut_fix.csv")

demo_path = Path("assets/demo.csv")

df_no_covid = pd.read_csv(file_path, low_memory=False)

# Create list of Morbidities
morbidity_list = list(df_no_covid['GENERAL_MORBIDITY'])

# Count the frequency of the morbidities
morbidity_counts = Counter(morbidity_list)

# Extract unique values and count occurrences
unique_values_counts = df_no_covid.groupby('GENERAL_MORBIDITY')['CASE_NUMBER'].nunique()

# Sort unique values by count (most occurrences to least)
sorted_unique_values_counts = unique_values_counts.sort_values(ascending=False)

# Create a list of tuples with (value, count)
sorted_unique_values_and_counts = [(value, count) for value, count in
                                   zip(sorted_unique_values_counts.index, sorted_unique_values_counts)]

# Print the list of tuples
# print(sorted_unique_values_and_counts)

strings_list = [f"{value}" for value, count in zip(sorted_unique_values_counts.index, sorted_unique_values_counts)]

# Calculate the sum of counts for each unique value

sorted_morbidity_list = sorted(unique_values_counts.keys(), key=lambda x: unique_values_counts[x], reverse=True)

# Sort options by the sum of counts (descending order)


# ---------------------------------------------------------------------------------
# Create the dropdown menu options
trend_options = [
    {'label': 'Daily', 'value': 1},
    {'label': '7 Day', 'value': 7},
    {'label': '30 Day', 'value': 30}
]
# ---------------------------------------------------------------------------------------
# Layout of the app
app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href="assets/css/style.css"
    ),
    html.Div([

        html.Div([
            # App Controls Section
            html.Div(
                id="app-controls",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    # Logo and Title
                                    html.Div(
                                        id="banner",
                                        className="banner",
                                        children=[
                                            html.Img(
                                                src="assets/images/wordcloud_morbidities.png",
                                                style={'width': 150, 'height': 150}
                                            ),
                                        ],
                                    ),
                                    html.Br(),
                                    html.Div(
                                        children=[
                                            html.H1(
                                                "Covid-Related Deaths Dashboard",
                                                style={'textAlign': 'center', 'color': '#ffffff', 'fontSize': 30,
                                                       'margin-left': '20px'}
                                            ),
                                            html.H1("Cook County, IL",
                                                    style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 22}),
                                        ], className="banner"
                                    )
                                ], className="banner", style={'display': 'flex'}
                            ),

                        ]
                    ),
                    html.Br(),
                    # Dropdowns and Checklists
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
                        start_date=df_no_covid['DATE_OF_DEATH'].min(),
                        end_date=dt(2022, 7, 1),
                        display_format='YYYY-MM-DD',
                        style={'textAlign': 'center', 'fontSize': 20, 'padding': 3, 'width': 400}
                    ),
                    html.Div([
                        html.Div(
                            children=[
                                html.P("Select a Sex:"),
                                dcc.Checklist(
                                    id='sex-select',
                                    options=[
                                        {
                                            "label": html.Div(['All Sexes'],
                                                              style={'color': '#dff4f5', 'fontSize': 20}),
                                            "value": 'All'
                                        },
                                        {
                                            "label": html.Div(['Female'], style={'color': '#dff4f5', 'fontSize': 20}),
                                            "value": 'Female'
                                        },
                                        {
                                            "label": html.Div(['Male'], style={'color': '#dff4f5', 'fontSize': 20}),
                                            "value": 'Male'
                                        },
                                    ],
                                    value=['All'],
                                    labelStyle={"display": "flex", "align-items": "left"},
                                    inline=True
                                ),
                                html.P("Select a Race:"),
                                dcc.Checklist(
                                    id='race-select',
                                    options=[
                                        {
                                            "label": html.Div(['All Races'],
                                                              style={'color': '#dff4f5', 'fontSize': 20}),
                                            "value": "All"
                                        },
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
                                            "label": html.Div(['Am. Indian'],
                                                              style={'color': '#dff4f5', 'fontSize': 20}),
                                            "value": "Am. Indian"
                                        },
                                        {
                                            "label": html.Div(['Unknown'], style={'color': '#dff4f5', 'fontSize': 20}),
                                            "value": "Unknown"
                                        }
                                    ],
                                    value=['All'],
                                    labelStyle={"display": "flex", "align-items": "center"},
                                )
                            ],

                        ),
                        html.Div(
                            children=[
                                html.Div([html.P("Select Age-Groups:"),
                                          dcc.Checklist(
                                              id='age-selections',
                                              options=[
                                                  {
                                                      "label": html.Div(['All Ages'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "All"
                                                  },
                                                  {
                                                      "label": html.Div(['< 18 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "< 18 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['19-29 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "19-29 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['30-39 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "30-39 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['40-49 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "40-49 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['50-59 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "50-59 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['60-69 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "60-69 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['70-79 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "70-79 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['80-89 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "80-89 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['90-99 Yrs'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "90-99 Yrs"
                                                  },
                                                  {
                                                      "label": html.Div(['100 Yrs <'],
                                                                        style={'color': '#dff4f5', 'fontSize': 20}),
                                                      "value": "10O Yrs <"
                                                  },
                                              ],
                                              value=['All'],
                                              labelStyle={"display": "flex", "align-items": "center"},
                                          )], style={'paddingLeft': '25px', 'alignItems': 'center'})])
                    ], style={"display": "flex", 'alignItems': 'center'}),
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
                className='app-controls',
                style={'display': 'flex', 'height': '100vh', 'width': '30vw', "align-items": "center"}
            ),

            # Graphs Section
            html.Div(
                id="app-graphs",
                children=[
                    dcc.Tabs(
                        id='tabs-select',
                        value='tab-1',
                        children=[
                            dcc.Tab(label='Per Capita', value='Per Capita'),
                            dcc.Tab(label='Total', value='tab-2'),
                        ]),
                    html.Div(id='output-container')],
                className='app-graphs'

            ),
        ], style={'display': 'flex', 'height': '100vh', 'width': '100vw'})
    ], style={'display': 'flex', 'height': '100vh', 'width': '100vw'})
])


@app.callback(
    [Output(component_id='output-container', component_property='children')],
    [Input(component_id='morbidity-select', component_property='value'),
     Input(component_id='trend-statistics', component_property='value'),
     Input(component_id='date-slider', component_property='start_date'),
     Input(component_id='date-slider', component_property='end_date'),
     Input(component_id='age-selections', component_property='value'),
     Input(component_id='sex-select', component_property='value'),
     Input(component_id='race-select', component_property='value'),
     Input(component_id='tabs-select', component_property='value'),
     ])
def rolling_trends(morbidity, time_span, start_date, end_date, age, sex, race, tabs):
    # Filter data based on selected date range
    if tabs == 'Per Capita':
        filtered_df = df_no_covid[(pd.to_datetime(df_no_covid['DATE_OF_DEATH']) >= pd.to_datetime(start_date)) & (
                pd.to_datetime(df_no_covid['DATE_OF_DEATH']) <= pd.to_datetime(end_date))]
    else:
        filtered_df = df_no_covid[(pd.to_datetime(df_no_covid['DATE_OF_DEATH']) >= pd.to_datetime(start_date)) & (
                pd.to_datetime(df_no_covid['DATE_OF_DEATH']) <= pd.to_datetime(end_date))]
    # Filter out NA in column
    # filtered_df['GENDER'] = filtered_df['GENDER'].dropna()
    # Filter to set NA to All
    # filtered_df['RACE'] = filtered_df['RACE'].fillna('All')

    filtered_data = filtered_df.groupby(['DATE_OF_DEATH', 'AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY'])[
        'CASE_NUMBER'].nunique().reset_index()

    fig = make_subplots(rows=1, cols=1, subplot_titles=(""))

    if time_span == 1:
        fig.update_layout(title_text="Daily Total Deaths")
        for group in age:
            age_data = filtered_data[filtered_data['AGE_GROUP'] == group]
            for gender in sex:
                sex_data = age_data[age_data['GENDER'] == gender]
                for races in race:
                    race_data = sex_data[sex_data['RACE'] == races]
                    for morbid in morbidity:
                        morbid_data = race_data[race_data['GENERAL_MORBIDITY'] == morbid]
                        trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'], mode='lines',
                                           name=f"{group}-{races}-{gender}-{morbid}")
                        fig.add_trace(trace)
    elif time_span == 7:
        fig.update_layout(title_text="7 Day Rolling Average of Total Deaths")
        for group in age:
            age_data = filtered_data[filtered_data['AGE_GROUP'] == group]
            for gender in sex:
                sex_data = age_data[age_data['GENDER'] == gender]
                for races in race:
                    race_data = sex_data[sex_data['RACE'] == races]
                    for morbid in morbidity:
                        morbid_data = race_data[race_data['GENERAL_MORBIDITY'] == morbid]
                        morbid_data['ROLLING_AVG'] = morbid_data.groupby(['AGE_GROUP', 'GENDER', 'GENERAL_MORBIDITY'])[
                            'CASE_NUMBER'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
                        morbid_data['ROLLING_AVG'] = morbid_data['ROLLING_AVG'].fillna(0)
                        trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['ROLLING_AVG'], mode='lines',
                                           name=f"{group}-{races}-{gender}-{morbid}")
                        fig.add_trace(trace)
    else:
        fig.update_layout(title_text="30 Day Rolling Average of Total Deaths")
        for group in age:
            age_data = filtered_data[filtered_data['AGE_GROUP'] == group]
            for gender in sex:
                sex_data = age_data[age_data['GENDER'] == gender]
                for races in race:
                    race_data = sex_data[sex_data['RACE'] == races]
                    for morbid in morbidity:
                        morbid_data = race_data[race_data['GENERAL_MORBIDITY'] == morbid]
                        morbid_data['ROLLING_AVG'] = \
                            morbid_data.groupby(['AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY'])[
                                'CASE_NUMBER'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
                        morbid_data['ROLLING_AVG'] = morbid_data['ROLLING_AVG'].fillna(0)
                        trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['ROLLING_AVG'], mode='lines',
                                           name=f"{group}-{races}-{gender}-{morbid}")
                        fig.add_trace(trace)

    fig.update_xaxes(title_text='Date of Death')
    fig.update_yaxes(title_text='Deaths')
    fig.update_layout(showlegend=True)
    fig.update_layout(width=1000, height=600)
    fig.update_layout(legend=dict(x=1, y=1, xanchor='left', yanchor='top', traceorder='normal'))
    fig.update_layout(legend={'title': 'Age-Race-Gender-Category'})

    return [dcc.Graph(figure=fig)]


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
