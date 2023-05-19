import dash_bootstrap_components as dbc
from dash import Dash, page_container, page_registry, html

LOGO = 'https://i.ibb.co/v1SzKZj/social-sleuth.png'

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

navbar = dbc.Row(
            [
            dbc.Navbar(
                    [
                    # Logo Column
                    html.Div(
                        html.A(
                            html.Img(src=LOGO, height="100px"),
                            href="/",
                            style={"textDecoration": "none"},
                        ),
                    ),

                    # Brand Column
                    html.Div(
                        dbc.NavbarBrand(
                            "Sentiment Analytics",
                            className="d-flex align-items-center",
                            style={
                                "height": "80px",
                                "color": "#f5f5f5",
                                "font-size": "40px",  # Change this value to your preferred font size
                                "font-family": "Helvetica Neue"  # Change this value to your preferred font type
                            }
                        ),

                        className='text-center',  # add this line to center content
                    ),

                    # Navigation Items Column
                    html.Div(
                        [
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        "Reddit",
                                        href="https://www.reddit.com/r/technology/",
                                        target="_blank",
                                        style={"color": "#f5f5f5",
                                               "font-size": "15px",
                                               "font-family": "Verdana"}
                                    ),
                                    dbc.DropdownMenu(
                                        children=[
                                            dbc.DropdownMenuItem(
                                                page["name"],
                                                href=page["relative_path"],
                                            )
                                            for page in page_registry.values()
                                        ],
                                        #class_name="mr-1",
                                        label="Menu",
                                        align_end=True,
                                    ),
                                ],
                            ),
                        ],
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
    app.run_server(debug=True)
