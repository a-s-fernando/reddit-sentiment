import dash_bootstrap_components as dbc
from dash import Dash, page_container, page_registry, html

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
                            dbc.Button("Home page", href="/",
                                       className="custom-button"),
                            dbc.Button("About us", href="/about_us",
                                       className="custom-button"),
                            dbc.Button("Keywords", href="/Visualisation",
                                       className="custom-button"),
                            dbc.Button("Leaderboard", href="/Leaderboard",
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
    ],
    style={"backgroundColor": "#f0f0f0f0"},
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)
