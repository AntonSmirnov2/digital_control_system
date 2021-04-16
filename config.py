import os

import dash_bootstrap_components as dbc
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    API_BOT_TOKEN = os.environ.get('API_BOT_TOKEN') or 'telegram-bot-api-token'
    APP_URL = os.environ.get('APP_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = os.path.join(basedir, 'app', 'static')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    DASH_EXTERNAL_STYLESHEETS = [
        dbc.themes.BOOTSTRAP,
        dict(href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
             rel="stylesheet")]

    ACTIONS_PER_PAGE = 50
