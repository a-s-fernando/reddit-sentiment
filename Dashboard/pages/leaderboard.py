from dash import register_page, dcc, html, callback
from data import build_dataframe
from datetime import datetime
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import spacy

nlp = spacy.load('en_core_web_sm')

register_page(__name__, title="Leaderboard", path='/Leaderboard')

data = build_dataframe().drop('comment_keyword', axis=1).drop_duplicates()


def is_organisation(x):
    if x == 'Bi-Weekly':
        return None
    doc = nlp(x)
    if len(doc.ents) == 0:
        return None
    entity = doc.ents[0]
    if entity.label_ != 'ORG':
        return None
    return entity.text


data['post_keyword'] = data['post_keyword'].apply(is_organisation)
data.dropna()


def filter_data(filtered_data):
    grouped_data = filtered_data.groupby(
        [filtered_data['comment_time'].dt.date, filtered_data['post_keyword']])['sentiment'].mean()
    grouped_data = grouped_data.to_frame().reset_index(level=[0, 1])
    grouped_data['comment_time'] = pd.to_datetime(grouped_data['comment_time'])
    return grouped_data


radioitems = dbc.RadioItems(
    options=[
        {"label": "Positive", "value": 1},
        {"label": "Negative", "value": -1},
    ],
    value=1,
    id="radioitems",
)

layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H3('Keyword Leaderboard'),
                                ],
                                width=6
                            ),
                            dbc.Col(
                                [
                                    radioitems
                                ],
                                width=6
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id='graph',
                                                        style={
                                                            'width': '100%', 'height': 'auto'}
                                                    ),
                                                ]
                                            )
                                        ],
                                        body=True
                                    )
                                ],
                                width=12
                            )
                        ],
                        justify="center",
                    )
                ]
            ),
            className="w-100",
        ),
    ],
    style={"color": "#000000"}
)


@callback(
    Output('graph', 'figure'),
    Input('radioitems', 'value'),
)
def generate_leaderboard(value):

    grouped_data = filter_data(data)
    sorted_data = grouped_data.sort_values(ascending=True, by='sentiment')

    if value == 1:
        leaders = sorted_data.tail(10)['post_keyword']
    else:
        leaders = sorted_data.head(10)['post_keyword']

    # Make the organizations distinct before plotting
    leaders = leaders.drop_duplicates()

    fig = go.Figure()

    for organization in leaders:
        organization_data = grouped_data[grouped_data['post_keyword']
                                         == organization]
        # Check if the organization has more than one data point
        if len(organization_data) > 1:
            fig.add_trace(go.Scatter(
                x=organization_data['comment_time'], y=organization_data['sentiment'], name=organization))

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Sentiment',
        title='Organisations Sentiment Over Time'
    )

    return fig
