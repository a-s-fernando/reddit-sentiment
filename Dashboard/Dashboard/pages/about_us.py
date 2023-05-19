import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import register_page

register_page(__name__, title="Our Team", path='/about_us')


layout = html.Div([
    dbc.Row([
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3('The Team'),
                    dbc.Row(
                        [
                            dbc.Col([
                                dbc.Card(
                                    [
                                        dbc.CardImg(
                                            src="https://ca.slack-edge.com/T04KPHPF6E8-U04KP1HH858-3a7173cf3c7a-512", top=True),
                                        dbc.CardBody(
                                            [
                                                html.H4("Adam - Project Lead",
                                                        className="card-title"),
                                                html.P(
                                                    """Adam is a highly skilled and experienced project manager with a proven track record of success.
                                        He is proficient in all aspects of the project management process, including planning, execution, delivery, and closure.
                                        He is also an excellent communicator, team player, problem solver, and leader.""",
                                                    className="card-text",
                                                )
                                            ]
                                        ),
                                    ],
                                    style={"width": "22rem"}
                                )
                            ],
                                width="auto"),

                            dbc.Col([
                                dbc.Card(
                                    [
                                        dbc.CardImg(
                                            src="https://ca.slack-edge.com/T04KPHPF6E8-U04K8F5CLUF-004369590d12-512", top=True),
                                        dbc.CardBody(
                                            [
                                                html.H4("Toby - Quality Assurance",
                                                        className="card-title"),
                                                html.P(
                                                    """Toby is a skilled QA specialist with a deep understanding of the QA process.
                                        He is able to identify and resolve defects quickly and efficiently, and he is an excellent communicator.
                                        Toby is a valuable asset to our team and is sure to be a key contributor to the success of our products.""",
                                                    className="card-text",
                                                )
                                            ]
                                        ),
                                    ],
                                    style={"width": "22rem"},
                                )
                            ],
                                width="auto"),

                            dbc.Col([
                                dbc.Card(
                                    [
                                        dbc.CardImg(
                                            src="https://ca.slack-edge.com/T04KPHPF6E8-U04KP1J15M0-edb3e7e72dae-512", top=True),
                                        dbc.CardBody(
                                            [
                                                html.H4("Alain - Architect",
                                                        className="card-title"),
                                                html.P(
                                                    """Alain is a skilled Cloud Architect with experience in designing, developing, and deploying cloud-based solutions.
                                        He is proficient in a variety of cloud technologies, including AWS and Terraform.
                                        Alain is also a skilled problem solver and is able to identify and resolve complex technical issues.""",
                                                    className="card-text",
                                                )
                                            ]
                                        ),
                                    ],
                                    style={"width": "22rem"},
                                )
                            ],
                                width="auto")
                        ],
                        justify="center",
                    ),
                    html.Br(),
                    html.H3('The Mission'),
                    html.Div(
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    """This project uses the Reddit API to extract comments about various entities, such as companies or concepts.
                            The sentiment of these comments is then analyzed over time to track changes in public opinion.
                            This information can be used to make informed decisions about marketing, product development, and other business initiatives.""",
                                    title="What does this do?"
                                ),
                                dbc.AccordionItem(
                                    """Our aim is to analyse how sentiment changes over time for various entities such as individuals, companies, technologies, and locations.
                            We believe that visualizing sentiment trends can be a powerful way to communicate our findings to our users.
                            By creating clear and concise visualizations, we can help our users understand how sentiment is changing for the entities that they care about.
                            This information can help our users make better decisions about their own businesses, investments, and personal lives.""",
                                    title="What are the goals?"
                                ),
                                dbc.AccordionItem(
                                    """
                            This tool can be used by organizations to gauge sentiment on other companies, products, and potential technologies. This information can be useful for informing design and business decisions.
                            For example, an organization could use this tool to see what people are saying about their competitors' products, or to get feedback on a new product that they are developing.
                            This tool can also be used by people who are simply curious about the world around them.
                            The information provided can provide fascinating cultural and societal insights. For example, someone could use this tool to see what people are saying about a current event, or to learn about different technologies.""",
                                    title="Who is it for?"
                                ),
                            ],
                            start_collapsed=True,
                        ),
                    )
                ]
            ),
            className="w-75 mb-3",
        ),
    ],
        justify="center"),
],
    style={"color": "#000000"},)
