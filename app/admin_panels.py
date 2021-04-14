from flask import url_for
from flask_admin import Admin
from flask_login import current_user
from flask_admin import AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
from wtforms import PasswordField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, AnyOf

from app import app, db
from app.models import User, Role, Action, Book, BookStatus, Company

# TODO add filtration to book page and button for each book with url to it page


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')


class MyModelView(ModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')


class UserModelView(MyModelView):
    column_exclude_list = ('password_hash',)
    form_excluded_columns = ('actions', 'password_hash', 'last_seen')
    form_columns = ('username', 'email', 'reset_password', 'telegram_id', 'company', 'access_role')
    form_args = {
        'username': {'validators': [DataRequired()]},
        'email': {'validators': [Email(), DataRequired()]},
    }
    form_extra_fields = {
        'reset_password': PasswordField('Reset password')
    }

    def on_model_change(self, form, model, is_created):
        if form.reset_password.data:
            model.password_hash = generate_password_hash(form.reset_password.data)

    def __init__(self, session):
        # Just call parent class with predefined model.
        super(UserModelView, self).__init__(User, session)


class ActionModelView(MyModelView):
    can_create = False
    column_default_sort = ('timestamp', True)

    def __init__(self, session):
        # Just call parent class with predefined model.
        super(ActionModelView, self).__init__(Action, session)


class MainIndexLink(MenuLink):
    def get_url(self):
        return url_for("index")


admin = Admin(app, index_view=MyAdminIndexView(endpoint='admin'))
admin.add_view(UserModelView(db.session))
admin.add_view(MyModelView(Book, db.session))
admin.add_view(ActionModelView(db.session))
admin.add_view(MyModelView(BookStatus, db.session, category='Types'))
admin.add_view(MyModelView(Company, db.session, category='Types'))
admin.add_view(MyModelView(Role, db.session, category='Types'))
admin.add_link(MainIndexLink(name='Main Page'))
