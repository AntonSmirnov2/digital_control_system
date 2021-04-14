import plotly.graph_objects as go

from app.plugins.db_helpers import get_all_subcontractors_short_names, get_all_valid_book_statuses, \
    get_books_count_by_status_for_scs, get_books_count_by_status

color_pallet = [
    "rgb(255,247,251)",
    "rgb(236,231,242)",
    "rgb(6, 214, 160)",  #
    "rgb(208,209,230)",
    "rgb(166,189,219)",
    "rgb(116,169,207)",
    "rgb(54,144,192)",
    "rgb(5,112,176)",
    "rgb(4,90,141)",
    "rgb(2,56,88)",
]
color_pallet.reverse()


def distribution_by_status_pie_fig():
    statuses = get_all_valid_book_statuses()
    values = get_books_count_by_status()
    fig_pie = go.Figure(data=[
        go.Pie(labels=statuses,
               values=values,
               hole=0.6,
               textinfo='value+percent',
               sort=False,
               marker={'colors': color_pallet})
    ])
    fig_pie.update_layout(
        legend=dict(orientation="h",
                    xanchor="center",
                    x=0.5),
        margin=dict(l=5, r=5, t=5, b=5),
        annotations=[dict(text=f'{sum(values)} шт.', x=0.5, y=0.5, font_size=20, showarrow=False)])
    return fig_pie


def distribution_by_subcontractors_bar_fig():
    statuses = get_all_valid_book_statuses()
    subcontractors = get_all_subcontractors_short_names()
    fig_bar = go.Figure(data=[
        go.Bar(name=status_name,
               x=subcontractors,
               y=get_books_count_by_status_for_scs(status_name),
               marker_color=color_pallet[i])
        for i, status_name in enumerate(statuses)
    ])
    fig_bar.update_layout(
        legend=dict(orientation="h",
                    xanchor="center",
                    x=0.5),
        margin=dict(l=5, r=5, t=5, b=5),
        barmode='stack', )
    return fig_bar
