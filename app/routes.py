from datetime import datetime

from flask import render_template, url_for, redirect
from flask import request, flash
from flask_login import login_user, logout_user, login_required, current_user
import telebot

from app import app, db, bot, API_BOT_TOKEN
from app.forms import LoginForm
from app.models import User, Action, Book
from config import Config

# TODO create view for book with info about it and moving story on map (far future)
# TODO add support to create several isolated projects with their own books, users and statistic (far future)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    # TODO refactor page, maybe replace it by "user" or "statistic"
    users = User.query.all()
    return render_template('index.html', title='Home', users=users)


@app.route('/user/<username>')
@login_required
def user(username):
    # TODO refactor user page for more nice view
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    actions = user.actions.order_by(Action.timestamp.desc()).paginate(page, app.config['ACTIONS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=actions.next_num) if actions.has_next else None
    prev_url = url_for('user', username=user.username, page=actions.prev_num) if actions.has_prev else None
    return render_template('user.html', user=user, actions=actions.items, title=username,
                           next_url=next_url, prev_url=prev_url)


@app.route('/book/<book_qr_id>')
@login_required
def book(book_qr_id):
    book = Book.query.filter_by(qr_id=book_qr_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    actions = book.actions.order_by(Action.timestamp.desc()).paginate(page, app.config['ACTIONS_PER_PAGE'], False)
    next_url = url_for('book', username=book.qr_id, page=actions.next_num) if actions.has_next else None
    prev_url = url_for('book', username=book.qr_id, page=actions.prev_num) if actions.has_prev else None
    return render_template('book.html', book=book, actions=actions.items, title='Book',
                           next_url=next_url, prev_url=prev_url)


@app.route('/delete_user/<username>')
@login_required
def delete_user(username):
    if current_user.access_role.role_name != 'admin':
        flash('Sorry, you can not delete users')
        return redirect(url_for('user'))
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid username')
        return redirect(url_for('user'))
    db.session.delete(user)
    db.session.commit()
    flash('User was deleted')
    return redirect(url_for('index'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #  TODO edit password and profile info
    return render_template('edit_profile.html', title='Edit Profile')


@app.route('/info')
def info():
    # TODO fill info page
    return render_template('info.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=remember_me)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sing In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route(f'/{API_BOT_TOKEN}', methods=['POST'])
def get_bot_update():
    if request.method == 'POST':
        r = request.get_json()
        update = telebot.types.Update.de_json(r)
        bot.process_new_updates([update])
        return 'OK', 200


@app.route('/webhook')
@login_required
def set_webhook():
    if Config.APP_URL:
        bot.remove_webhook()
        bot.set_webhook(Config.APP_URL + '/' + API_BOT_TOKEN)
        return 'OK', 200


@app.route('/dash/<dash_name>')
@login_required
def render_dashboard(dash_name):
    return redirect(f'/dashboard/{dash_name}')
