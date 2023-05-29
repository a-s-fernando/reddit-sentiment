""" Dash application for visualisations based on Social Sleuth data."""
import dash_bootstrap_components as dbc
from dash import Dash, page_container, html, callback, dcc, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from data import build_dataframe

DATA = build_dataframe().drop('comment_keyword', axis=1).drop_duplicates()
LOGO = 'https://i.ibb.co/G3gjvcb/Screenshot-2023-05-24-at-15-03-40.png'

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

navbar = dbc.Row(
    [
        dbc.Navbar(
            [
                # Logo Column
                html.Div(
                    html.A(
                        html.Img(src=LOGO, height="40px"),
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                ),

                # Navigation Items Column
                html.Div(
                    dbc.ButtonGroup(
                        [
                            dbc.Button("Home", href="/",
                                       className="custom-button"),
                            dbc.Button("About us", href="/about_us",
                                       className="custom-button"),
                            dbc.Button("Keywords", href="/keywords",
                                       className="custom-button"),
                            dbc.Button("Leaderboard", href="/leaderboard",
                                       className="custom-button"),
                        ],
                        className="mr-2",
                    ),
                ),
            ],
        ),
    ]
)


app.layout = dbc.Container(
    [
        navbar,
        page_container,
        html.Div(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Row([
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id='bottom-input',
                                            type='text',
                                            placeholder='Enter keywords (comma-separated)',
                                        )
                                    ], align='center'
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            'Search', id='bottom-search-button', color="primary", n_clicks=0, class_name='custom-button')
                                    ], align='center'
                                ),
                                dbc.Col(
                                    [
                                        dbc.Row([
                                            dcc.DatePickerSingle(
                                                id="bottom-datepicker",
                                                min_date_allowed=min(
                                                    DATA["comment_time"].dt.date),
                                                clearable=False,
                                            ),
                                        ],
                                            justify='end')
                                    ], width='auto'
                                ),

                            ],
                            style={'padding-bottom': '16px'}
                            ),
                            html.Div(
                                id="post-titles",
                            ),
                        ], title="Get Post Titles for a Date"
                    ),

                ],
                start_collapsed=True,
            ),
        ),
    ],
    style={"backgroundColor": "#f0f0f0f0"},
)


@callback(
    Output('post-titles', 'children'),
    Input('bottom-search-button', 'n_clicks'),
    State('bottom-input', 'value'),
    State('bottom-datepicker', 'date'),
)
def return_posts(n_clicks: int, keywords: str, date: str) -> list:
    """Return a list of post titles and their counts."""
    if keywords:

        # Split the keywords by comma
        keywords = [keyword.strip() for keyword in keywords.split(",")]
        # Filter the data based on the keywords
        filtered_data = DATA[DATA['post_keyword'].str.contains(
            '|'.join(keywords), case=False)]
        grouped_data = filtered_data.groupby(
            [filtered_data['comment_time'].dt.date, filtered_data['title']])['comment'].count()
        grouped_data = grouped_data.to_frame().reset_index(level=[0,1])
        grouped_data['comment_time'] = pd.to_datetime(grouped_data['comment_time'])
        filtered_data = grouped_data[(grouped_data['comment_time'] == date)]
        filtered_data = filtered_data.groupby(
            [filtered_data['title']])['comment'].sum()
        filtered_data = filtered_data.to_frame().reset_index(level=[0])
        filtered_data = filtered_data.sort_values(by='comment', ascending=False).rename(columns={"title": "Post Title", "comment": "Comment Count"})
        output = dash_table.DataTable(filtered_data.to_dict('records'),
                                      [{"name": i, "id": i} for i in filtered_data.columns],
                                      style_data={
                                        'whiteSpace': 'normal',
                                        'height': 'auto',
                                        'lineHeight': '15px'
                                        },
                                      style_cell={'textAlign': 'left'},)
        return output
    else:
        return []


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)
