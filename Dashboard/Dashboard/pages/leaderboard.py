import dash_html_components as html
from dash import register_page

register_page(__name__, title="Leaderboard", path='/Leaderboard')

layout = html.Div([
    html.H3('keyword-leaderboard')
])
