"""Page for visualisation of top (or bottom) 10 organisations based on average sentiment."""
import os
import json
from dash import register_page, dcc, html, callback
from data import build_dataframe
from datetime import datetime
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import spacy
import boto3
import dash_loading_spinners as dls

BUCKET_NAME = os.environ.get("bucket_name")
s3 = boto3.resource(service_name='s3', region_name=os.environ.get("region_name"),
                    aws_access_key_id=os.environ.get("access_key"), aws_secret_access_key=os.environ.get("secret_access_key"))
BUCKET = s3.Bucket(BUCKET_NAME)
FILE_KEY = "cache.json"
FILE_PATH = '/tmp/cache.json'
MODEL_SIZE = 'en_core_web_sm'
nlp = spacy.load(MODEL_SIZE)
data = build_dataframe().drop('comment_keyword', axis=1).drop_duplicates()

# Check if a remote cache exists, else create one afresh
cache = None
try:
    BUCKET.download_file(FILE_KEY, FILE_PATH)
    with open(FILE_PATH) as cache_file:
        cache = json.loads(cache_file.read())
except:
    cache = {}


register_page(__name__, title="Leaderboard", path='/Leaderboard')


def is_organisation(x):
    global cache
    if x == 'Bi-Weekly':
        return None
    if x not in cache:
        doc = nlp(x)
        if len(doc.ents) == 0:
            return None
        entity = doc.ents[0]
        cache[x] = entity.label_
        if entity.label_ != 'ORG':
            return None
        return x
    if cache[x] == 'ORG':
        return x
    return None


data['post_keyword'] = data['post_keyword'].apply(is_organisation)
data.dropna()
BUCKET.put_object(
    Key="cache.json", Body=json.dumps(cache))


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
    inline=True
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
                                    radioitems
                                ],
                                width="auto"
                            ),
                        ], justify="center",
                        style={"padding-bottom": "12px"}
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
                                                            id='graph',
                                                            style={
                                                                'width': '100%', 'height': 'auto'}
                                                        ),
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
def generate_leaderboard(value: int) -> go.Figure:
    """Depending on the inputted value, returns the 10 organisations with either the best or worst average sentiment."""

    grouped_data = filter_data(data)

    leaders = None
    if value == 1:
        leaders = grouped_data.sort_values(
            ascending=False, by='sentiment')['post_keyword']
    else:
        leaders = grouped_data.sort_values(
            ascending=True, by='sentiment')['post_keyword']

    # Make the organizations distinct before plotting
    leaders = leaders.drop_duplicates()

    fig = go.Figure()

    count = 0
    for organization in leaders:
        organization_data = grouped_data[grouped_data['post_keyword']
                                         == organization]
        # Check if the organization has more than one data point
        if len(organization_data) > 1:
            fig.add_trace(go.Scatter(
                x=organization_data['comment_time'], y=organization_data['sentiment'], name=organization))
            count += 1
        if count == 10:
            break

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Sentiment',
        title='Organisations Sentiment Over Time'
    )

    return fig
