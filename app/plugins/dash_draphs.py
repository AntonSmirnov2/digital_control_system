from datetime import datetime, timedelta

import plotly.graph_objects as go

from app.plugins.db_helpers import get_all_subcontractors_short_names, get_all_valid_book_statuses, \
    get_books_count_by_status_for_scs, get_books_count_by_status, get_actions_in_period

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
        barmode='stack',
        plot_bgcolor='white'
    )
    return fig_bar


def _create_timeline_from_unit(time_unit, period):
    if time_unit == 'week':
        return [(datetime.utcnow() - timedelta(days=i * 7)).strftime('%Ww %yy') for i in range(period)]
    if time_unit == 'day':
        return [(datetime.utcnow() - timedelta(days=i)).strftime('%d.%m.%y') for i in range(period)]
    if time_unit == 'hwr':
        return [(datetime.utcnow() - timedelta(hours=i)).strftime('%H:00 %d.%m') for i in range(period)]


def actions_per_unit_bar_fig(time_unit, period=24):
    unit_names = _create_timeline_from_unit(time_unit, period)
    unit_names.reverse()
    actions_count = get_actions_in_period(time_unit, period)
    bar_width = 0.2
    fig_bar = go.Figure(data=[
        go.Bar(name='Прогресс',
               x=unit_names,
               y=actions_count['progress'],
               width=bar_width,
               marker_color=color_pallet[2]),
        go.Bar(name='Регресс',
               x=unit_names,
               y=actions_count['regress'],
               width=bar_width,
               marker_color='red'),
        go.Bar(name='Удаление',
               x=unit_names,
               y=actions_count['delete'],
               width=bar_width,
               marker_color='gray'),
        go.Bar(name='Создание',
               x=unit_names,
               y=actions_count['create'],
               width=bar_width,
               marker_color='gray'),
    ])
    y_axis_max = max([i + j for i, j in zip(actions_count['progress'], actions_count['create'])])
    y_axis_min = min([i + j for i, j in zip(actions_count['regress'], actions_count['delete'])])
    if (y_axis_max + abs(y_axis_min)) < 35:
        fig_bar.update_yaxes(range=[-5, 30])
    fig_bar.update_layout(
        legend=dict(yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01),
        margin=dict(l=5, r=5, t=5, b=5),
        barmode='relative',
        plot_bgcolor='white'
    )
    return fig_bar
