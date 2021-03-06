from app import bot, db
from app.models import User
from app.plugins.bot_markups import start_markup, update_location_markup
from app.plugins.bot_logic import decrypt_photo, callback_to_dict, render_html_for_tg, \
    download_photo
from app.plugins.db_helpers import get_tg_user, update_book_status, get_book_status_and_real_id,\
    logout_tg_user, update_book_location, get_possible_location_updates, get_book_status_name_by_id
from app.plugins.bot_decorators import send_action, catch_error, is_authenticated

# TODO create handler for text input of QR-code [in: "AGPZ-000123", out: query to db]
# TODO refactor BOT for work with sessions from db
# TODO add simple queries to db [e.g. show last location]

tg_user = {}


@bot.message_handler(commands=['start', 'help'])
@send_action('typing')
@catch_error()
@is_authenticated()
def command_start_handler(message):
    cid = message.chat.id
    uid = message.from_user.id
    user_tg_name = message.from_user.first_name
    user = get_tg_user(uid)
    markup = start_markup(user.access_role.role_name)
    bot.send_message(cid, f'С возвращением, {user_tg_name}!', reply_markup=markup)


@bot.message_handler(content_types=['location'])
@catch_error()
@is_authenticated()
def location(message):
    cid = message.chat.id
    uid = message.from_user.id
    mid = message.id
    user = get_tg_user(uid)
    lat = message.location.latitude
    long = message.location.longitude
    bot.delete_message(cid, mid)
    locations = get_possible_location_updates(user)
    reply_msg = render_html_for_tg('locations.html', locations=locations)
    markup = update_location_markup(lat, long)
    bot.send_message(cid, reply_msg, reply_markup=markup, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: '&timestamp=' in call.data)
@catch_error()
def update_book_location_callback(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    answer = callback_to_dict(call.data)
    bot.delete_message(cid, mid)
    if answer['timestamp'] != '0':
        user = get_tg_user(cid)
        from_time = answer['timestamp']
        new_location = f'{answer["lat"]} {answer["long"]}'
        updates_count = update_book_location(user, from_time, new_location)
        bot.answer_callback_query(call.id, 'Геолокация обновлена')
        bot.send_message(cid, f'Геолокация обновлена у {updates_count} поз.')
    else:
        bot.answer_callback_query(call.id, 'Отмена изменений')


@bot.message_handler(commands=['Logout'])
@catch_error()
def logout_user(message):
    cid = message.chat.id
    uid = message.from_user.id
    user = get_tg_user(uid)
    if not user:
        bot.send_message(cid, 'Вы уже не зарегистрированы в системе.')
        return
    logout_tg_user(user)
    markup = start_markup('new_user')
    bot.send_message(cid, 'Вы вышли из аккаунта.', reply_markup=markup)


@bot.message_handler(commands=['Login'])
@catch_error()
def login_user(message):
    cid = message.chat.id
    uid = message.from_user.id
    user = get_tg_user(uid)
    if user:
        markup = start_markup(user.access_role.role_name)
        bot.send_message(cid, 'Вы уже зарегистрированы в системе.', reply_markup=markup)
        return
    msg = bot.send_message(cid, 'Введите логин:')
    bot.register_next_step_handler(msg, login_input)


@catch_error()
def login_input(message):
    cid = message.chat.id
    uid = message.from_user.id
    mid = message.id
    username = message.text
    bot.delete_message(cid, mid)
    user = User.query.filter_by(username=username).first()
    if not user:
        markup = start_markup('new_user')
        bot.send_message(cid, 'Неверный логин. Нажмите /Login для новой попытки.', reply_markup=markup)
        return
    tg_user[uid] = username
    msg = bot.send_message(cid, 'Введите пароль:')
    bot.register_next_step_handler(msg, register_user)


@catch_error()
def register_user(message):
    cid = message.chat.id
    uid = message.from_user.id
    mid = message.id
    username = tg_user[uid]
    password = message.text
    bot.delete_message(cid, mid)
    user = User.query.filter_by(username=username).first()
    if not user.check_password(password):
        markup = start_markup('new_user')
        bot.send_message(cid, 'Неверный пароль. Нажмите /Login для новой попытки.', reply_markup=markup)
        return
    user.telegram_id = uid
    db.session.commit()
    markup = start_markup(user.access_role.role_name)
    bot.send_message(cid, f'Вход выполнен.', reply_markup=markup)


@bot.message_handler(commands=['Info'])
@send_action('typing')
@catch_error()
@is_authenticated()
def send_info(message):
    cid = message.chat.id
    uid = message.from_user.id
    name = message.from_user.first_name
    user = get_tg_user(uid)
    reply_msg = render_html_for_tg('info.html', username=name, new_user=False)
    markup = start_markup(user.access_role.role_name)
    bot.send_message(cid, reply_msg, reply_markup=markup, parse_mode='HTML')


@bot.message_handler(commands=['Statistic'])
@send_action('typing')
@catch_error()
@is_authenticated()
def send_info(message):
    cid = message.chat.id
    uid = message.from_user.id
    user = get_tg_user(uid)
    if user.access_role.role_name in ['manager', 'admin']:
        markup = start_markup(user.access_role.role_name)
        reply_msg = render_html_for_tg('statistic.html')
        bot.send_message(cid, reply_msg, reply_markup=markup, parse_mode='HTML')


@bot.message_handler(content_types=['photo'])
@send_action('typing')
@catch_error()
@is_authenticated()
def encrypt_photo(message):
    # TODO add possibility for handling several QR-codes in one time
    cid = message.chat.id
    mid = message.id
    download_photo(message)
    bot.delete_message(cid, mid)
    reply_msg, markup = decrypt_photo()
    bot.send_message(cid, reply_msg, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: '&new_status=' in call.data)
@catch_error()
def update_book_status_callback(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    reply = callback_to_dict(call.data)
    bot.delete_message(cid, mid)
    if reply['new_status'] != '0':
        user = get_tg_user(cid)
        update_book_status(user, reply['qr_id'], int(reply['new_status']))
        bot.answer_callback_query(call.id, 'Статус обновлен')
        new_status, real_id = get_book_status_and_real_id(reply['qr_id'])
        old_status = get_book_status_name_by_id(reply['old_status'])
        reply_msg = render_html_for_tg('book_status_updated.html',
                                       real_id=real_id,
                                       old_status=old_status,
                                       new_status=new_status)
        bot.send_message(cid, reply_msg, parse_mode='html')
    else:
        bot.answer_callback_query(call.id, 'Отмена изменений')


@bot.message_handler(func=lambda message: True)
@send_action('typing')
def echo_reply(message):
    cid = message.chat.id
    bot.send_message(cid, message.text)
