# pages/page1.py
import dash_html_components as html
from dash import register_page

register_page(__name__, title="Homepage", path='/')

layout = html.Div([
    html.H3('Homepage')
])
