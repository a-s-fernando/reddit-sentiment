from io import BytesIO
import base64
from dash import register_page, dcc, html, callback
import json
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from data import build_dataframe
import plotly.express as px
import pandas as pd
from PIL import Image
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

register_page(__name__, title="Visualisations", path='/Visualisation')
DATA = build_dataframe()  # Load the data (replace with your actual data loading code)


def dataframe_to_string(dataframe: pd.DataFrame) -> str:
    """Turns a column of strings into one string"""
    text = ''
    for ind in dataframe.index:
        text += dataframe['comment_keyword'][ind] + ' '
    return text[:-1]

def filter_dataframe(df: pd.DataFrame, keyword: str, positive: bool) -> pd.DataFrame:
    """returns a dataframe that has been filtered"""
    lower_keyword = keyword.lower()
    if positive:
        series = df['sentiment'] > 0
    else:
        series = df['sentiment'] < 0
    return df.loc[(df['post_keyword'] == keyword) & (series) & (df['comment_keyword'] != lower_keyword)].reset_index()

def mask_selector(positive: bool):
    if positive:
        image = Image.open("./assets/happy.png")
    else:
        image = Image.open("./assets/sad.jpeg")
    return np.array(image)

def key_word_cloud(df: pd.DataFrame, keyword: str, positive: bool):
    """takes a post keyword and sentiment and produces a wordcloud"""
    filtered_df = filter_dataframe(df, keyword, positive)
    text = dataframe_to_string(filtered_df)
    wc = WordCloud(
        mask=mask_selector(positive),
        font_path='./assets/RomanVibes.otf',
        width=800,
        height=600,
        min_font_size=14,
        background_color="#000000",
        colormap="gist_rainbow_r"
    ).generate(text)

    return wc


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H3('Keyword Visualisations'),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Input(
                                                id='input',
                                                type='text',
                                                placeholder='Enter keywords (comma-separated)',
                                            )
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button('Search', id='search-button', color="primary", n_clicks=0)
                                        ]
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    html.H4("Positive Word Cloud"),

                                                    html.Img(
                                                        id='positive-wordcloud',
                                                        style={'width': '100%', 'height': 'auto'}
                                                    ),
                                                ],
                                                body=True
                                            )
                                        ],
                                        width=6  # Adjust the width to fit two word clouds side by side
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.Row([
                                                        html.H4("Negative Word Cloud"),
                                                    ],
                                                    justify='center'),
                                                    html.Img(
                                                        id='negative-wordcloud',
                                                        style={'width': '100%', 'height': 'auto'}
                                                    ),
                                                ],
                                                body=True
                                            )
                                        ],
                                        width=6  # Adjust the width to fit two word clouds side by side
                                    )
                                ],
                                justify="center",
                            )
                        ]
                    ),
                    className="w-100",
                ),
            ],
            justify="center"
        ),
    ],
    style={"color": "#000000"}
)



@callback(
    Output('positive-wordcloud', 'src'),
    Output('negative-wordcloud', 'src'),
    Input('search-button','n_clicks'),
    State('input', 'value')
)
def update_wordclouds(n_clicks, keyword):
    if n_clicks > 0 and keyword:
        positive_img, negative_img = BytesIO(), BytesIO()
        key_word_cloud(DATA, keyword, positive=True).to_image().save(positive_img, format='PNG')
        key_word_cloud(DATA, keyword, positive=False).to_image().save(negative_img, format='PNG')
        return 'data:image/png;base64,{}'.format(base64.b64encode(positive_img.getvalue()).decode()), 'data:image/png;base64,{}'.format(base64.b64encode(negative_img.getvalue()).decode())
    else:
        return None, None


# if __name__ == "__main__":
#     DATA = build_dataframe()
#     key_word_cloud(DATA, 'happy', sentiment=True)
