import dash_table as dt

data_management_table = dt.DataTable(
    id='data_management_table',
    columns=[],
    data=[],
    editable=True,
    export_headers='display',
    page_size=500,
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
    row_deletable=True,
    fixed_rows={'headers': True},
    style_cell={
        'minWidth': 95, 'maxWidth': 95, 'width': 95
    },
    style_table={'height': '85vh', "maxHeight": '85vh'}
)