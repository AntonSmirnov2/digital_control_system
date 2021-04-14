from datetime import datetime, timedelta

from telebot import types
from keyboa import keyboa_maker

from app.models import BookStatus


def start_markup(user_type):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btns = []
    if user_type == 'user':
        btns.append(types.KeyboardButton(text='/Location', request_location=True))
        btns.append(types.KeyboardButton(text='/Info'))
        btns.append(types.KeyboardButton(text='/Logout'))
    elif user_type == 'manager':
        btns.append(types.KeyboardButton(text='/Location', request_location=True))
        btns.append(types.KeyboardButton(text='/Statistic'))
        btns.append(types.KeyboardButton(text='/Info'))
        btns.append(types.KeyboardButton(text='/Logout'))
    elif user_type == 'admin':
        btns.append(types.KeyboardButton(text='/Location', request_location=True))
        btns.append(types.KeyboardButton(text='/Statistic'))
        btns.append(types.KeyboardButton(text='/Info'))
        btns.append(types.KeyboardButton(text='/Logout'))
    else:
        btns.append(types.KeyboardButton(text='/Login'))
        btns.append(types.KeyboardButton(text='/Info'))
    markup.add(*btns)
    return markup


def change_book_status_markup(current_status, qr_id):
    btns = []
    book_statuses = BookStatus.query.all()
    old_status = ''
    for status in book_statuses:
        if status.status_name == current_status:
            btns.append({f'🟢 {status.status_name}': '0'})
            old_status = status.id
        else:
            btns.append({f'⚪ {status.status_name}': status.id})
    btns.append({'отмена': '0'})
    return keyboa_maker(items=btns, items_in_row=2,
                        front_marker=f'&qr_id={qr_id}&old_status={old_status}&new_status=')


def update_location_markup(lat, long):
    now = datetime.utcnow()
    fmt = '%d/%m/%Y, %H:%M:%S'
    btns = [
        {'1 час': (now - timedelta(hours=1)).strftime(fmt)},
        {'3 часа': (now - timedelta(hours=3)).strftime(fmt)},
        {'12 часов': (now - timedelta(hours=12)).strftime(fmt)},
        {'1 день': (now - timedelta(days=1)).strftime(fmt)},
        {'1 неделя': (now - timedelta(days=7)).strftime(fmt)},
        {'отмена': '0'}
    ]
    return keyboa_maker(items=btns, items_in_row=2,
                        front_marker=f'&lat={lat}&long={long}&timestamp=')
