from functools import wraps

from app import bot
from config import Config
from app.plugins.db_helpers import get_tg_user
from app.plugins.bot_logic import render_html_for_tg
from app.plugins.bot_markups import start_markup


def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(message, *args, **kwargs):
            bot.send_chat_action(chat_id=message.chat.id, action=action)
            return func(message, *args, **kwargs)
        return command_func
    return decorator


def catch_error():
    def decorator(func):
        @wraps(func)
        def command_func(message, *args, **kwargs):
            try:
                return func(message, *args, **kwargs)
            except Exception as e:
                if Config.DEBUG:
                    bot.send_message(message.chat.id, e)
                else:
                    bot.send_message(message.chat.id, 'Упс, что-то пошло не так.')
        return command_func
    return decorator


def is_authenticated():
    def decorator(func):
        @wraps(func)
        def command_func(message, *args, **kwargs):
            user = get_tg_user(message.from_user.id)
            if user:
                return func(message, *args, **kwargs)
            reply_msg = render_html_for_tg('info.html', username=message.from_user.first_name, new_user=True)
            markup = start_markup('new_user')
            bot.send_message(message.chat.id, reply_msg, reply_markup=markup, parse_mode='HTML')
        return command_func
    return decorator
