from dash import register_page, html

register_page(__name__, title="Our Team", path='/about_us')


layout = html.Div([
    html.H3('About us')
],
style={"color": "#000000"},)
