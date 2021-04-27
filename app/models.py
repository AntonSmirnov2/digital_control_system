from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(30), nullable=False)

    users = db.relationship('User', backref='access_role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.id}:{self.role_name}>'


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_full_name = db.Column(db.String(120), nullable=False)
    org_short_name = db.Column(db.String(20), nullable=False)
    org_type = db.Column(db.String(20), nullable=False)

    books = db.relationship('Book', backref='company', lazy='dynamic')
    users = db.relationship('User', backref='company', lazy='dynamic')

    def __repr__(self):
        return f'<Org. {self.id}:{self.org_short_name}>'


class BookStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(60), nullable=False)
    status_duration = db.Column(db.Interval, nullable=False, default=timedelta(days=99999), server_default='99999')

    books = db.relationship('Book', backref='book_status', lazy='dynamic')

    def __repr__(self):
        return f'<BookStatus {self.id}:{self.status_name}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    telegram_id = db.Column(db.Integer)

    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    user_role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    user_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    actions = db.relationship('Action', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.id}:{self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return role == Role.query.get(self.user_role_id).role_name


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    location = db.Column(db.String(30))

    old_status_id = db.Column(db.Integer, db.ForeignKey('book_status.id'))
    new_status_id = db.Column(db.Integer, db.ForeignKey('book_status.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    old_status = db.relationship('BookStatus', foreign_keys=[old_status_id])
    new_status = db.relationship('BookStatus', foreign_keys=[new_status_id])

    def __repr__(self):
        return f'<Action {self.id}:{self.action}>'


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_id = db.Column(db.String(20), index=True, unique=True)
    real_id = db.Column(db.String(140))

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('book_status.id'))
    actions = db.relationship('Action', backref='book', lazy='dynamic')

    def __repr__(self):
        return f'<Book {self.id}:{self.real_id}>'
