from datetime import date
import base64
import io
import pandas as pd
from random import randint
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table as dt
import dash_extensions as de
from dash.dependencies import Input, Output

from app import dash, db
from app.models import Book
from app.plugins.dash_tables import data_management_table

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 50,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    # "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Statistic", href='/dashboard/statistic', external_link=True)),
        dbc.NavItem(dbc.NavLink("Main Page", href='/', external_link=True)),
    ],
    brand="DCS data",
    brand_href='/',
    sticky="top",
)

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.Button(
                    'Загрузить БД',
                    id='upload_data_button',
                    outline=True,
                    color="primary",
                    className="m-3",
                    block=True),
                dbc.Button(
                    'Скачать шаблон',
                    id='download_data_button',
                    outline=True,
                    color="primary",
                    className="m-3",
                    block=True,
                ),
                dcc.Download(id='download_data'),
                dbc.Button(
                    'Очистить таблицу',
                    id='clear_data_button',
                    outline=True,
                    color="danger",
                    className="m-3",
                    block=True,
                    disabled=True
                ),
                dcc.Upload([
                    dbc.Button(
                        'Загрузить из файла',
                        id='file_upload_data_button',
                        outline=True,
                        color="primary",
                        className="mr-3",
                        block=True,),
                ], id='table_file_upload', className="mr-3 ml-3 mt-3")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id='dynamic-sidebar',
    style=SIDEBAR_STYLE,
)

df = pd.DataFrame()

content = html.Div(
    id="page-content",
    children=[data_management_table],
    style=CONTENT_STYLE)

layout = html.Div([
    navbar,
    sidebar,
    content
])


@dash.callback(
    Output('download_data', 'data'),
    Input('download_data_button', 'n_clicks'),
    prevent_initial_call=True)
def download_table(n_clicks):
    global df
    return dcc.send_data_frame(df.to_excel, f"dcs_database-{date.today()}.xlsx", sheet_name="Database")


@dash.callback(
    Output('data_management_table', 'data'),
    Output('data_management_table', 'columns'),
    Output('data_management_table', 'row_deletable'),
    Output('download_data_button', 'children'),
    Output('clear_data_button', 'disabled'),
    Output('upload_data_button', 'n_clicks'),
    Output('clear_data_button', 'n_clicks'),
    Input('upload_data_button', 'n_clicks'),
    Input('clear_data_button', 'n_clicks'))
def upload_db_to_table(upload_click, clear_click):
    global df
    df = pd.read_sql(Book.query.statement, db.session.bind)
    df = df.sort_values('id')
    columns = [{'name': i, 'id': i} for i in df.columns]
    if upload_click:
        data = df.to_dict('records')
        name_download_button = 'Скачать данные'
        disable_clear_button = False
        row_deletable = False
    else:
        df = df.iloc[0:0]
        data = [{k["id"]: '' for k in columns} for i in range(5)]
        name_download_button = 'Скачать шаблон'
        disable_clear_button = True
        row_deletable = True
    return data, columns, row_deletable, \
           name_download_button, disable_clear_button, \
           None, None
