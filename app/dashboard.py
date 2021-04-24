import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import dash
from app.plugins import dash_statistic_page, dash_data_management_page


dash.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ]
)


@dash.callback(Output('page-content', 'children'),
               Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/dashboard/statistic':
        return dash_statistic_page.layout
    elif pathname == '/dashboard/data_management':
        return dash_data_management_page.layout
    else:
        return '404'
