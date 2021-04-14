import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import dash
from app.plugins.dash_draphs import distribution_by_status_pie_fig, distribution_by_subcontractors_bar_fig


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Info", href='/info', external_link=True)),
        dbc.NavItem(dbc.NavLink("Main Page", href='/', external_link=True)),
    ],
    brand="DCS statistic page",
    brand_href='/',
    sticky="top",
)

action_menu = dbc.Button(
    'Обновить значения',
    id='update_button',
    outline=True,
    color="primary",
    className="mr-3",
    block=True
)

pie_graph_card = dbc.Card([
    dbc.CardHeader('Комплекты по статусам', style={'text-align': 'center'}),
    dbc.CardBody([
        dcc.Graph(id='pie-graph')
    ]),
], style={'margin': 0})

bar_graph_card = dbc.Card([
    dbc.CardHeader('Комплекты по подрядчикам', style={'text-align': 'center'}),
    dbc.CardBody([
        dcc.Graph(id='bar-graph')
    ])
], style={'margin': 0})

pie_and_bar_graph = dbc.Row([
    dbc.Col(pie_graph_card, width=5),
    dbc.Col(bar_graph_card, width=7)]
)

dash.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                # dcc.Interval(id="interval", interval=5000, n_intervals=0),
                action_menu,
                html.Br(),
                pie_and_bar_graph,
                html.Br(),
                html.Div(style={"height": "200px"}),
            ]
        ),
    ]
)

@dash.callback(
    [Output('pie-graph', 'figure'),
     Output('bar-graph', 'figure')],
    [Input('update_button', 'n_clicks'),
     ]
)
def update_statistic(update):
    return distribution_by_status_pie_fig(), distribution_by_subcontractors_bar_fig()
