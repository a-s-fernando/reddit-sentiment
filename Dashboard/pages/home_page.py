import random
from dash import register_page, dcc, html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from data import build_dataframe
from datetime import datetime
import plotly.express as px
import pandas as pd

# Load the data
data = build_dataframe().drop('comment_keyword', axis=1).drop_duplicates()


# Register the page
register_page(__name__, title="Homepage", path='/')
random_selector = ["Netflix", "Apple", "OpenAI", "ChatGPT"]


def filter_data(keywords):
    # Filter the data based on the provided keywords
    if keywords:
        # Split the keywords by comma
        keywords = [keyword.strip() for keyword in keywords.split(",")]
        # Filter the data based on the keywords
        filtered_data = data[data['post_keyword'].str.contains(
            '|'.join(keywords), case=False)]

    else:
        # Return the original data if no keywords are provided
        filtered_data = data
    grouped_data = filtered_data.groupby(
        [filtered_data['comment_time'].dt.date, filtered_data['title']])['sentiment'].mean()
    grouped_data = grouped_data.to_frame().reset_index(level=[0, 1])
    grouped_data['comment_time'] = pd.to_datetime(grouped_data['comment_time'])

    return grouped_data


layout = html.Div([
    html.H3('Homepage'),
    dbc.Row([
            dbc.Col([
                dbc.Input(
                    id='input',
                    type='text',
                    placeholder='Enter keywords (comma-separated)',
                    value=random.choice(random_selector)
                )
            ]),
            dbc.Col([
                dbc.Button('Search', id='search-button',
                           color="primary", n_clicks=0)
            ]),
            ]),

    dbc.Row([
            dbc.Col(width=3,
                    children=[
                        dcc.DatePickerRange(
                            id="datepicker",
                            min_date_allowed=min(data["comment_time"].dt.date),
                            end_date=max(data["comment_time"].dt.date),
                            start_date=min(data["comment_time"].dt.date),
                            clearable=False,
                        ),
                    ]),
            dbc.Col([
                dcc.Graph(id="time-graph")
            ])
            ]),
])


@callback(
    Output('time-graph', 'figure'),
    Input('search-button', 'n_clicks'),
    State('datepicker', 'start_date'),
    State('datepicker', 'end_date'),
    State('input', 'value')
)
def search_keywords(n_clicks, start_date, end_date, keywords):
    if not keywords or not start_date or not end_date:
        return px.scatter()  # Return an empty scatter plot or a default figure
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    filtered_data = filter_data(keywords)
    filtered_data = filtered_data[
        (filtered_data['comment_time'] >= start_date) & (
            filtered_data['comment_time'] <= end_date)
    ]

    # Perform any necessary data processing and filtering here

    # Create the graph
    fig = px.line(filtered_data, x='comment_time', y='sentiment')
    return fig
