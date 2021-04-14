from flask import Flask
from dash import Dash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import telebot

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
dash = Dash(__name__,
            server=app,
            url_base_pathname='/dashboard/',
            external_stylesheets=Config.DASH_EXTERNAL_STYLESHEETS,
            assets_folder=Config.STATIC_FOLDER)

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
moment = Moment(app)

API_BOT_TOKEN = app.config['API_BOT_TOKEN']
bot = telebot.TeleBot(API_BOT_TOKEN)
bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

from app import routes, models, bot_commands, admin_panels, dash_pannel

# TODO mail
# TODO logging
# TODO deploy
