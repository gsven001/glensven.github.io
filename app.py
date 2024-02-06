from pathlib import Path
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from collections import Counter
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime as dt

# Define your CSS style sheets
external_css = [
    "assets/clinical-analytics.css",
    "assets/base.css",
]

# Initialize the Dash app
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                external_stylesheets=external_css)

server = app.server
app.config.suppress_callback_exceptions = True

# Set the title of the dashboard
app.title = "Covid-Related Deaths, Cook County, IL Dashboard"

# Create the dropdown menu options
trend_options = [
    {'label': 'Daily', 'value': 1},
    {'label': '7 Day', 'value': 7},
    {'label': '30 Day', 'value': 30}
]


def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Covid Dashboard"),
            html.H3("Cook County Covid Related Deaths Dashboard"),
            html.Div(
                id="intro",
                children="Explore the Cook County medical examiner database to determine the demographic characteristics of Covid-19 related deaths.",
                style={'fontSize': 14},
            ),
        ],
    )


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Br(),
            html.P("Select Daily, 7-Day, or 30-day Average"),
            dcc.Dropdown(
                id='trend-statistics',
                options=trend_options,
                value=30,
                placeholder='Select Rolling Window',
                clearable=False,
                style={'color': '#000000'}
            ),
            html.Br(),
            html.P("Select Date Range"),
            dcc.DatePickerRange(
                id="date-picker-select",
                start_date=df_no_covid['DATE_OF_DEATH'].min(),
                end_date=dt(2022, 7, 1),
                display_format='YYYY-MM-DD',
            ),
            html.Div(
                id="control-card-checks",
                children=[

                    html.Div(
                        [html.Br(),
                         html.P("Select a Sex:"),
                         dcc.Checklist(
                             id='sex-select',
                             options=[
                                 {
                                     "label": html.Div(['All Sexes'],
                                                       style={'fontSize': 14}),
                                     "value": 'All'
                                 },
                                 {
                                     "label": html.Div(['Female'], style={'fontSize': 14}),
                                     "value": 'Female'
                                 },
                                 {
                                     "label": html.Div(['Male'], style={'fontSize': 14}),
                                     "value": 'Male'
                                 },
                             ],
                             value=['All'],
                             labelStyle={"display": "flex"},
                             inline=True
                         ),
                         html.Br(),
                         html.P("Select a Race:"),
                         dcc.Checklist(
                             id='race-select',
                             options=[
                                 {
                                     "label": html.Div(['All Races'], style={'fontSize': 14}),
                                     "value": "All"
                                 },
                                 {
                                     "label": html.Div(['White'], style={'fontSize': 14}),
                                     "value": "White"
                                 },
                                 {
                                     "label": html.Div(['Black'], style={'fontSize': 14}),
                                     "value": "Black"
                                 },
                                 {
                                     "label": html.Div(['Asian'], style={'fontSize': 14}),
                                     "value": "Asian"
                                 },
                                 {
                                     "label": html.Div(['Other'], style={'fontSize': 14}),
                                     "value": "Other"
                                 }
                             ],
                             value=['All'],
                             labelStyle={"display": "flex"},
                         )
                         ])
                    ,
                    html.Div(
                        children=[
                            html.Div([html.Br(),
                                      html.P("Select Age-Groups:"),
                                      dcc.Checklist(
                                          id='age-selections',
                                          options=[
                                              {
                                                  "label": html.Div(['All Ages'], style={'fontSize': 14}),
                                                  "value": "All"
                                              },
                                              {
                                                  "label": html.Div(['< 18 Yrs'], style={'fontSize': 14}),
                                                  "value": "< 18 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['19-29 Yrs'], style={'fontSize': 14}),
                                                  "value": "19-29 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['30-39 Yrs'], style={'fontSize': 14}),
                                                  "value": "30-39 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['40-49 Yrs'], style={'fontSize': 14}),
                                                  "value": "40-49 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['50-59 Yrs'], style={'fontSize': 14}),
                                                  "value": "50-59 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['60-69 Yrs'], style={'fontSize': 14}),
                                                  "value": "60-69 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['70-79 Yrs'], style={'fontSize': 14}),
                                                  "value": "70-79 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['80-89 Yrs'], style={'fontSize': 14}),
                                                  "value": "80-89 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['90-99 Yrs'], style={'fontSize': 14}),
                                                  "value": "90-99 Yrs"
                                              },
                                              {
                                                  "label": html.Div(['100 Yrs <'], style={'fontSize': 14}),
                                                  "value": "100 Yrs <"
                                              },
                                          ],
                                          value=['All'],
                                          labelStyle={"display": "flex"}
                                      )])])

                ], style={"display": "flex"}
            ),
            html.Br(),
            html.P("Select General Morbidity Category"),
            dcc.Dropdown(
                id="morbidity-select",
                options=[{'label': value, 'value': value} for value in sorted_morbidity_list],
                value=sorted_morbidity_list[:1],
                placeholder="No General Morbidity Selected",
                searchable=True,
                clearable=False,
                multi=True,
                style={'color': '#000000'}
            )
        ]
    )


# Load Cook County Covid Mortality Data
file_path = Path("assets/final_covid_2.csv")

demo_path = Path("assets/demo.csv")

df_covid = pd.read_csv(file_path, low_memory=False)

df_no_covid = df_covid[df_covid['GENERAL_MORBIDITY'] != 'COVID-19']

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

# Layout of the app
app.layout = html.Div(
    id="app-container",
    children=[
        html.Div([
            # App Controls Section
            html.Div(
                id="app-controls",
                children=[
                    # Banner
                    # html.Div(
                    #     id="banner",
                    #     className="banner",
                    #     children=[html.Img(src=app.get_asset_url("plotly_logo.png"))],
                    # ),
                    # Left column
                    html.Div(
                        id="left-column",
                        className="four columns",
                        children=[description_card(), generate_control_card()]
                    ),
                    # Graphs Section
                    html.Div(
                        id="right-column",
                        className="eight columns",
                        children=[
                            html.Div([
                                dcc.Tabs(
                                    id='tabs-select',
                                    value='Per Capita',
                                    children=[
                                        dcc.Tab(label='Per Capita', value='Per Capita',
                                                style={'borderBottom': '1px solid #d6d6d6',
                                                       'padding': '5px',
                                                       'fontWeight': 'bold'}),
                                        dcc.Tab(label='Total', value='Total',
                                                style={'borderBottom': '1px solid #d6d6d6',
                                                       'padding': '5px',
                                                       'fontWeight': 'bold'}),
                                    ], className="custom-tabs", style={'width': '300px', 'height': '50px'})
                            ], className="dash-tab"),
                            html.Div(id='output-container', style={'alignItems': 'center'}),
                            html.Div(id='output-container-2')],
                        style={'alignItems': 'center'},
                        # className='app-graphs'

                    ),
                ])
        ])
    ])


def filter_data_by_date_range(df, start_date, end_date):
    date_filter = (pd.to_datetime(df['DATE_OF_DEATH']) >= pd.to_datetime(start_date)) & (
            pd.to_datetime(df['DATE_OF_DEATH']) <= pd.to_datetime(end_date))

    return df_no_covid[date_filter]


@app.callback(
    [Output(component_id='output-container', component_property='children')],
    [Input(component_id='morbidity-select', component_property='value'),
     Input(component_id='trend-statistics', component_property='value'),
     Input(component_id='date-picker-select', component_property='start_date'),
     Input(component_id='date-picker-select', component_property='end_date'),
     Input(component_id='age-selections', component_property='value'),
     Input(component_id='sex-select', component_property='value'),
     Input(component_id='race-select', component_property='value'),
     Input(component_id='tabs-select', component_property='value'),
     ])
def rolling_trends(morbidity, time_span, start_date, end_date, age, sex, race, tabs):
    filtered_df = filter_data_by_date_range(df_covid, start_date, end_date)

    filtered_data = \
        filtered_df.groupby(['DATE_OF_DEATH', 'AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY', 'TOTAL_POP'])[
            'CASE_NUMBER'].nunique().reset_index()

    filtered_data['PER_CAP'] = (filtered_data['CASE_NUMBER'] / filtered_data['TOTAL_POP']) * 100000

    filtered_data_bar = filtered_df.groupby(['AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY', 'TOTAL_POP'])[
        'CASE_NUMBER'].nunique().reset_index()

    filtered_data_bar['PER_CAP'] = (filtered_data_bar['CASE_NUMBER'] / filtered_data_bar['TOTAL_POP']) * 100000

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
                        if tabs == 'Per Capita':
                            if (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All') & (
                                    gender == 'All'):
                                x_label = f"Total Pop."
                            elif (morbid.title() == 'All Deaths') & (group == 'All') & (gender == 'All'):
                                x_label = f"{races} Pop."
                            elif (morbid.title() == 'All Deaths') & (races == 'All') & (gender == 'All'):
                                x_label = f"{group} Pop."
                            elif (group == 'All') & (races == 'All') & (gender == 'All'):
                                x_label = f"Pop. with {morbid.title()}"
                            elif (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All'):
                                x_label = f"{gender} Pop."
                            elif (morbid.title() == 'All Deaths') & (group == 'All'):
                                x_label = f"{gender}, {races} Pop."
                            elif morbid.title() == 'All Deaths':
                                x_label = f"Ages: {group} for {gender}, {races} Pop."
                            else:
                                x_label = f"Ages: {group} for {gender}, {races} Pop. with {morbid.title()}"
                            trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['PER_CAP'],
                                               mode='lines',
                                               name=x_label)
                            fig.update_yaxes(title_text='Deaths Per Capita (Deaths Per 100,000)')
                            fig.update_layout(title_text="Total Daily Deaths per Capita")
                        else:
                            if (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All') & (
                                    gender == 'All'):
                                x_label = f"Total Pop."
                            elif (morbid.title() == 'All Deaths') & (group == 'All') & (gender == 'All'):
                                x_label = f"{races} Pop."
                            elif (morbid.title() == 'All Deaths') & (races == 'All') & (gender == 'All'):
                                x_label = f"{group} Pop."
                            elif (group == 'All') & (races == 'All') & (gender == 'All'):
                                x_label = f"Pop. with {morbid.title()}"
                            elif (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All'):
                                x_label = f"{gender} Pop."
                            elif (morbid.title() == 'All Deaths') & (group == 'All'):
                                x_label = f"{gender}, {races} Pop."
                            elif morbid.title() == 'All Deaths':
                                x_label = f"Ages: {group} for {gender}, {races} Pop."
                            else:
                                x_label = f"Ages: {group} for {gender}, {races} Pop. with {morbid.title()}"
                            trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['CASE_NUMBER'],
                                               mode='lines',
                                               name=x_label)
                            fig.update_layout(title_text="Total Deaths")
                            fig.update_yaxes(title_text='Deaths')
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
                        if tabs == 'Per Capita':
                            morbid_data.loc[:, 'ROLLING_AVG'] = \
                                morbid_data.groupby(['AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY'])[
                                    'PER_CAP'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
                            fig.update_yaxes(title_text='Deaths Per Capita (Deaths Per 100,000)')
                            fig.update_layout(title_text="7 Day Rolling Average of Total Deaths per Capita")
                        else:
                            morbid_data['ROLLING_AVG'] = \
                                morbid_data.groupby(['AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY'])[
                                    'CASE_NUMBER'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
                            fig.update_yaxes(title_text='Deaths')
                            fig.update_layout(title_text="7 Day Rolling Average of Total Deaths")
                        # morbid_data[:, 'ROLLING_AVG'] = morbid_data['ROLLING_AVG'].fillna(0)
                        if (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All') & (gender == 'All'):
                            x_label = f"Total Pop."
                        elif (morbid.title() == 'All Deaths') & (group == 'All') & (gender == 'All'):
                            x_label = f"{races} Pop."
                        elif (morbid.title() == 'All Deaths') & (races == 'All') & (gender == 'All'):
                            x_label = f"{group} Pop."
                        elif (group == 'All') & (races == 'All') & (gender == 'All'):
                            x_label = f"Pop. with {morbid.title()}"
                        elif (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All'):
                            x_label = f"{gender} Pop."
                        elif (morbid.title() == 'All Deaths') & (group == 'All'):
                            x_label = f"{gender}, {races} Pop."
                        elif morbid.title() == 'All Deaths':
                            x_label = f"Ages: {group} for {gender}, {races} Pop."
                        else:
                            x_label = f"Ages: {group} for {gender}, {races} Pop. with {morbid.title()}"
                        trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['ROLLING_AVG'], mode='lines',
                                           name=x_label)
                        fig.add_trace(trace)
    else:
        for group in age:
            age_data = filtered_data[filtered_data['AGE_GROUP'] == group]
            for gender in sex:
                sex_data = age_data[age_data['GENDER'] == gender]
                for races in race:
                    race_data = sex_data[sex_data['RACE'] == races]
                    for morbid in morbidity:
                        morbid_data = race_data[race_data['GENERAL_MORBIDITY'] == morbid]
                        if tabs == 'Per Capita':
                            morbid_data.loc[:, 'ROLLING_AVG'] = \
                                morbid_data.groupby(['AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY'])[
                                    'PER_CAP'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
                            fig.update_yaxes(title_text='Deaths Per Capita (Deaths Per 100,000)')
                            fig.update_layout(title_text="30 Day Rolling Average of Total Deaths per Capita")
                        else:
                            morbid_data['ROLLING_AVG'] = \
                                morbid_data.groupby(['AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY'])[
                                    'CASE_NUMBER'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
                            fig.update_yaxes(title_text='Deaths')
                            fig.update_layout(title_text="30 Day Rolling Average of Total Deaths")
                        morbid_data.loc[:, 'ROLLING_AVG'] = morbid_data['ROLLING_AVG'].fillna(0)
                        if (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All') & (gender == 'All'):
                            x_label = f"Total Pop."
                        elif (morbid.title() == 'All Deaths') & (group == 'All') & (gender == 'All'):
                            x_label = f"{races} Pop."
                        elif (morbid.title() == 'All Deaths') & (races == 'All') & (gender == 'All'):
                            x_label = f"{group} Pop."
                        elif (group == 'All') & (races == 'All') & (gender == 'All'):
                            x_label = f"Pop. with {morbid.title()}"
                        elif (morbid.title() == 'All Deaths') & (group == 'All') & (races == 'All'):
                            x_label = f"{gender} Pop."
                        elif (morbid.title() == 'All Deaths') & (group == 'All'):
                            x_label = f"{gender}, {races} Pop."
                        elif morbid.title() == 'All Deaths':
                            x_label = f"Ages: {group} for {gender}, {races} Pop."
                        else:
                            x_label = f"Ages: {group} for {gender}, {races} Pop. with {morbid.title()}"
                        trace = go.Scatter(x=morbid_data['DATE_OF_DEATH'], y=morbid_data['ROLLING_AVG'], mode='lines',
                                           name=x_label)
                        fig.add_trace(trace)

    fig.update_xaxes(title_text='Date of Death')
    fig.update_layout(showlegend=True)
    fig.update_layout(width=1200, height=600)
    fig.update_layout(legend=dict(x=1, y=1, xanchor='left', yanchor='top', traceorder='normal'))
    fig.update_layout(legend={'title': 'Demographic Group'})

    return [dcc.Graph(figure=fig)]


@app.callback(
    [Output(component_id='output-container-2', component_property='children')],
    [Input(component_id='morbidity-select', component_property='value'),
     Input(component_id='date-picker-select', component_property='start_date'),
     Input(component_id='date-picker-select', component_property='end_date'),
     Input(component_id='age-selections', component_property='value'),
     Input(component_id='sex-select', component_property='value'),
     Input(component_id='race-select', component_property='value'),
     Input(component_id='tabs-select', component_property='value'),
     ])
def bar_functions(morbidity, start_date, end_date, age, sex, race, tabs):
    filtered_df = filter_data_by_date_range(df_no_covid, start_date, end_date)

    filtered_data_bar = filtered_df.groupby(['AGE_GROUP', 'RACE', 'GENDER', 'GENERAL_MORBIDITY', 'TOTAL_POP'])[
        'CASE_NUMBER'].nunique().reset_index()

    filtered_data_bar['PER_CAP'] = (filtered_data_bar['CASE_NUMBER'] / filtered_data_bar['TOTAL_POP']) * 100000

    fig = make_subplots(rows=1, cols=1, subplot_titles=(""))

    for index, row in filtered_data_bar[
        filtered_data_bar['AGE_GROUP'].isin(age) & filtered_data_bar['RACE'].isin(race) & filtered_data_bar[
            'GENDER'].isin(sex) & filtered_data_bar['GENERAL_MORBIDITY'].isin(morbidity)].iterrows():
        if (row['GENERAL_MORBIDITY'].title() == 'All Deaths') & (row['AGE_GROUP'] == 'All') & (row['RACE'] == 'All') & (
                row['GENDER'] == 'All'):
            x_label = f"Total Pop."
        elif (row['GENERAL_MORBIDITY'].title() == 'All Deaths') & (row['AGE_GROUP'] == 'All') & (
                row['GENDER'] == 'All'):
            x_label = f"{row['RACE']} Pop."
        elif (row['GENERAL_MORBIDITY'].title() == 'All Deaths') & (row['RACE'] == 'All') & (row['GENDER'] == 'All'):
            x_label = f"{row['AGE_GROUP']} Pop."
        elif (row['AGE_GROUP'] == 'All') & (row['RACE'] == 'All') & (row['GENDER'] == 'All'):
            x_label = f"Pop. with {row['GENERAL_MORBIDITY'].title()}"
        elif (row['GENERAL_MORBIDITY'].title() == 'All Deaths') & (row['AGE_GROUP'] == 'All') & (row['RACE'] == 'All'):
            x_label = f"{row['GENDER']} Pop."
        elif (row['GENERAL_MORBIDITY'].title() == 'All Deaths') & (row['AGE_GROUP'] == 'All'):
            x_label = f"{row['GENDER']}, {row['RACE']} Pop."
        elif row['GENERAL_MORBIDITY'].title() == 'All Deaths':
            x_label = f"Ages: {row['AGE_GROUP']} for {row['GENDER']}, {row['RACE']} Pop."
        else:
            x_label = f"Ages: {row['AGE_GROUP']} for {row['GENDER']}, {row['RACE']} Pop. with {row['GENERAL_MORBIDITY'].title()}"
        if tabs == 'Per Capita':
            fig.add_trace(go.Bar(
                x=[x_label],  # x-axis category for each row
                y=[row['PER_CAP']],  # value for each row
                alignmentgroup=True
            ))
            fig.update_layout(
                title='Total Deaths per Capita',
                xaxis_title='Demographic Group',
                yaxis_title='Deaths per Capita (Deaths per 100,000)',
                barmode='group',  # 'group' for grouped bars, 'stack' for stacked bars
            )
        else:
            fig.add_trace(go.Bar(
                x=[x_label],  # x-axis category for each row
                y=[row['CASE_NUMBER']],  # value for each row
                alignmentgroup=True
            ))
            fig.update_layout(
                title='Total Deaths',
                xaxis_title='Demographic Group',
                yaxis_title='Deaths',
                barmode='group',  # 'group' for grouped bars, 'stack' for stacked bars
            )

    fig.update_layout(showlegend=False)
    fig.update_layout(width=1200, height=600)
    fig.update_layout(legend=dict(x=1, y=1, xanchor='left', yanchor='top', traceorder='normal'))

    return [dcc.Graph(figure=fig)]


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
