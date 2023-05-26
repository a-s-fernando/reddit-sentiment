"""Main page featuring time vs sentiment vis for a single query."""
import random
from dash import register_page, dcc, html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from pandas import DataFrame
from data import build_dataframe
from datetime import datetime
import plotly.express as px
import pandas as pd
import dash_loading_spinners as dls
import plotly.graph_objects as go

# Load the data
data = build_dataframe().drop('comment_keyword', axis=1).drop_duplicates()


# Register the page
register_page(__name__, title="Home", path="/")
random_selector = ["Apple", "OpenAI, ChatGPT"]


def filter_data(keywords: str) -> DataFrame:
    """Filter the dataframe based on the provided keywords"""
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
        [filtered_data['comment_time'].dt.date])['sentiment'].mean()
    grouped_data = grouped_data.to_frame().reset_index(level=[0])
    grouped_data['comment_time'] = pd.to_datetime(grouped_data['comment_time'])
    return grouped_data


layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Input(
                                        id='input',
                                        type='text',
                                        placeholder='Enter keywords (comma-separated)',
                                        value=random.choice(random_selector),
                                    )
                                ], align='center'
                            ),
                            dbc.Col(
                                [
                                    dbc.Button(
                                        'Search', id='search-button', color="primary", n_clicks=0, class_name='custom-button')
                                ], align='center'
                            ),
                            dbc.Col(
                                [
                                    dbc.Row([
                                        dcc.DatePickerRange(
                                            id="datepicker",
                                            min_date_allowed=min(
                                                data["comment_time"].dt.date),
                                            end_date=max(
                                                data["comment_time"].dt.date),
                                            start_date=min(
                                                data["comment_time"].dt.date),
                                            clearable=False,
                                            calendar_orientation='vertical'
                                        ),
                                    ],
                                        justify='end')
                                ], width='auto'
                            ),
                        ],
                        style={'padding-bottom': '16px'}
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    dls.Hash(
                                                        dcc.Graph(
                                                            id="time-graph"),
                                                        color="#051923",
                                                        speed_multiplier=2,
                                                        size=100,
                                                    )
                                                ]
                                            )
                                        ],
                                        body=True
                                    )
                                ],
                            )
                        ],
                        className="mb-3",
                    )
                ]
            ),
            className="w-100",
        )
    ]
)


@callback(
    Output('time-graph', 'figure'),
    Input('search-button', 'n_clicks'),
    State('datepicker', 'start_date'),
    State('datepicker', 'end_date'),
    State('input', 'value')
)
def search_keywords(n_clicks: int, start_date: str, end_date: str, keywords: str) -> go.Figure:
    """Returns a line graph based on the given keywords, for data between a given time frame."""
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
    fig.update_layout(
        xaxis_title='Comment Time',
        yaxis_title='Sentiment',
    )
    fig.update_traces(line_color='#00A6FB')
    return fig

