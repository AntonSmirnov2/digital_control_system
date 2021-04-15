import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import dash
from app.plugins.dash_draphs import distribution_by_status_pie_fig, distribution_by_subcontractors_bar_fig

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.Button(
            'Обновить значения',
            id='update_button',
            outline=True,
            color="primary",
            className="mr-3",
            block=True)),
        dbc.NavItem(dbc.NavLink("Info", href='/info', external_link=True)),
        dbc.NavItem(dbc.NavLink("Main Page", href='/', external_link=True)),
    ],
    brand="DCS statistic page",
    brand_href='/',
    sticky="top",
)

total_distribution_pie_graph_card = dbc.Card([
    dbc.CardHeader('Комплекты по статусам', style={'text-align': 'center'}),
    dbc.CardBody([
        dcc.Graph(id='total-distribution-pie-graph')
    ]),
], style={'margin': 0})

subcontractors_distribution_bar_graph_card = dbc.Card([
    dbc.CardHeader('Комплекты по подрядчикам', style={'text-align': 'center'}),
    dbc.CardBody([
        dcc.Graph(id='subcontractors-distribution-bar-graph')
    ])
], style={'margin': 0})

distribution_pie_and_bar_graph = dbc.Row([
    dbc.Col(total_distribution_pie_graph_card, width=5),
    dbc.Col(subcontractors_distribution_bar_graph_card, width=7)
])

select = dbc.Select(
    id="select",
    bs_size='sm',
    options=[
        {"label": "Месяц", "value": "month"},
        {"label": "Неделю", "value": "week"},
        {"label": "День", "value": "day"},
    ],
    value='week'
)

apd_header = dbc.Row([
    dbc.Col('Активность за', width=2, align='center', style={'text-align': 'end'}),
    dbc.Col(select, width=2)
], justify="center", no_gutters=True)

actions_per_day_bar_graph_card = dbc.Card([
    dbc.CardHeader(apd_header),
    dbc.CardBody([
        dcc.Graph(id='actions-per-day-bar-graph')
    ])
], style={'margin': 0})

actions_per_day_bar_graph = dbc.Row([
    dbc.Col(actions_per_day_bar_graph_card, width=12)
])

dash.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                # dcc.Interval(id="interval", interval=5000, n_intervals=0),
                distribution_pie_and_bar_graph,
                html.Br(),
                actions_per_day_bar_graph,
                html.Br(),
                html.Div(style={"height": "200px"}),
            ]
        ),
    ]
)


@dash.callback(
    [Output('total-distribution-pie-graph', 'figure'),
     Output('subcontractors-distribution-bar-graph', 'figure')],
    [Input('update_button', 'n_clicks')]
)
def update_statistic(update):
    return distribution_by_status_pie_fig(), distribution_by_subcontractors_bar_fig()
