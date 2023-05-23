"""wordcloud visualisations page for dash application"""
from io import BytesIO
import base64
from dash import register_page, html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from data import build_dataframe
import pandas as pd
from PIL import Image
import numpy as np
from numpy import ndarray
from wordcloud import WordCloud
from pandas import DataFrame


register_page(__name__, title="Visualisations", path='/Visualisation')
DATA = build_dataframe()  # Load the data (replace with your actual data loading code)


def dataframe_to_set(dataframe: DataFrame) -> set[str]:
    """Turns a column of strings into one set of strings"""
    entries = set()
    for ind in dataframe.index:
        entries.add(dataframe['comment_keyword'][ind])
    return entries


def dataframe_to_list(dataframe: DataFrame) -> list[str]:
    """Turns a column of strings into one list of strings"""
    entries = []
    for ind in dataframe.index:
        entries.append(dataframe['comment_keyword'][ind])
    return entries


def filter_dataframe(df: DataFrame, keyword: str, positive: bool) -> DataFrame:
    """returns a dataframe that has been filtered"""
    if positive:
        series = df['sentiment'] > 0
    else:
        series = df['sentiment'] < 0
    df = df.drop(
        df[df['comment_keyword'].str.contains(f"{keyword} | fucking | fuck | fucks | shit | shitty", case=False)].index)
    return df.loc[(df['post_keyword'].str.contains(keyword, case=False) & (series))].reset_index()


def mask_selector(positive: bool) -> ndarray:
    """creates a mask for the wordcloud based on positivity"""
    if positive:
        image = Image.open("./assets/happy.png")
    else:
        image = Image.open("./assets/sad.jpeg")
    return np.array(image)


def filter_text(filtered, opposite, keyword) -> str:
    """filters text to make sure both wordclouds have unique words"""
    text = ''
    for word in filtered:
        if (word in opposite) or (keyword.lower() in word) or (len(word) < 1):
            continue
        else:
            text += word + ' '
    return text[:-1]


def generate_wordcloud(text: str, positive: bool) -> WordCloud:
    """create a wordcloud from text"""
    return WordCloud(
        mask=mask_selector(positive),
        font_path='./assets/RomanVibes.otf',
        width=800,
        height=600,
        min_font_size=14,
        background_color="#ffffff",
        colormap="autumn"
    ).generate(text)


def key_word_cloud(df: DataFrame, keyword: str, positive: bool):
    """takes a post keyword and sentiment and produces a wordcloud"""
    filtered_df = filter_dataframe(df, keyword, positive)
    if positive:
        opposite_df = filter_dataframe(df, keyword, False)
    else:
        opposite_df = filter_dataframe(df, keyword, True)
    opposite = dataframe_to_set(opposite_df)
    filtered = dataframe_to_list(filtered_df)
    text = filter_text(filtered, opposite, keyword)
    word_cloud = generate_wordcloud(text, positive)
    return word_cloud


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
                                                placeholder='Enter keyword',
                                                value='Apple'
                                            )
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                'Search', id='search-button', color="primary", n_clicks=0)
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
                                                    html.H4(
                                                        "Positive Word Cloud"),

                                                    html.Img(
                                                        id='positive-wordcloud',
                                                        style={
                                                            'width': '100%', 'height': 'auto'}
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
                                                        html.H4(
                                                            "Negative Word Cloud"),
                                                    ],
                                                        justify='center'),
                                                    html.Img(
                                                        id='negative-wordcloud',
                                                        style={
                                                            'width': '100%', 'height': 'auto'}
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
    Input('search-button', 'n_clicks'),
    State('input', 'value')
)
def update_wordclouds(n_clicks, keyword):
    if keyword:
        positive_img, negative_img = BytesIO(), BytesIO()
        key_word_cloud(DATA, keyword, positive=True).to_image().save(
            positive_img, format='PNG')
        key_word_cloud(DATA, keyword, positive=False).to_image().save(
            negative_img, format='PNG')
        return 'data:image/png;base64,{}'.format(base64.b64encode(positive_img.getvalue()).decode()), 'data:image/png;base64,{}'.format(base64.b64encode(negative_img.getvalue()).decode())
    else:
        return None, None
