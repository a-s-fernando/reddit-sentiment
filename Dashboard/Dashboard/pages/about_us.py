import dash_html_components as html
from dash import register_page

register_page(__name__, title="Our Team", path='/about_us')


layout = html.Div([
    html.H3('About us')
],
style={"color": "#000000"},)
