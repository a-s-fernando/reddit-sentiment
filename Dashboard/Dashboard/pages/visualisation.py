import dash_html_components as html
from dash import register_page

register_page(__name__, title="Visualisations", path='/Visualisation')

layout = html.Div([
    html.H3('keyword-visualisation')
])
