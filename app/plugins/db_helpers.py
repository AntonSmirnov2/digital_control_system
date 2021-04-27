from datetime import datetime, timedelta, date, time

from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Role, BookStatus, Action, Book, Company


def get_book_status_and_real_id(qr_id):
    """Возвращает наименование текущего статуса книги и ее шифр"""
    book = Book.query.filter_by(qr_id=qr_id).first()
    if book:
        real_id = book.real_id
        current_status = book.book_status.status_name
        return current_status, real_id


def get_book_status_name_by_id(id):
    return BookStatus.query.get(int(id)).status_name


def get_tg_user(tg_user_id) -> User:
    """Возвращает юзера по телеграм ID"""
    return User.query.filter_by(telegram_id=tg_user_id).first()


def logout_tg_user(user):
    """Переводит значение user.telegram_id в 0"""
    user.telegram_id = '0'
    db.session.commit()


def create_book(user, qr_id, real_id, company, status='Формирование', location='Неизвестно'):
    if isinstance(user, str):
        user = User.query.filter_by(username=user).first()
    if isinstance(status, str):
        status = BookStatus.query.filter_by(status_name=status).first()
    if isinstance(company, str):
        company = Company.query.filter_by(org_short_name=company).first()
    book = Book(qr_id=qr_id,
                real_id=real_id,
                book_status=status,
                company=company)
    db.session.add(book)
    db.session.commit()
    action = Action(action=f'{status.status_name} (Создание)',
                    location=location,
                    author=user,
                    book=book,
                    new_status=status)
    db.session.add(action)
    db.session.commit()


def update_book_status(user, book, status, location='Неизвестно'):
    if isinstance(user, str):
        user = User.query.filter_by(username=user).first()
    elif isinstance(user, int):
        user = User.query.filter_by(telegram_id=user).first()
    if isinstance(book, str):
        book = Book.query.filter_by(qr_id=book).first()
    if isinstance(status, str):
        status = BookStatus.query.filter_by(status_name=status).first()
    elif isinstance(status, int):
        status = BookStatus.query.get(status)
    old_status = book.book_status
    book.book_status = status
    action = Action(action=f'{old_status.status_name} -> {status.status_name}',
                    location=location,
                    author=user,
                    book=book,
                    old_status=old_status,
                    new_status=status)
    db.session.add(action)
    db.session.commit()


def update_book_location(user, from_time, location):
    from_time = datetime.strptime(from_time, '%d/%m/%Y, %H:%M:%S')
    user_actions = Action.query.filter_by(user_id=user.id).filter(Action.timestamp > from_time).all()
    updates_count = 0
    for action in user_actions:
        if action.location == '' or action.location == 'Неизвестно' or not action.location:
            action.location = location
            updates_count += 1
            db.session.commit()
    return updates_count


def get_possible_location_updates(user):
    now = datetime.utcnow()
    response = []
    my_time = {
        '1 час':    (now - timedelta(hours=1)),
        '3 часа':   (now - timedelta(hours=3)),
        '12 часов': (now - timedelta(hours=12)),
        '1 день':   (now - timedelta(days=1)),
        '1 неделя': (now - timedelta(days=7)),
        'Все время': (now - timedelta(days=1000))
    }
    for key, from_time in my_time.items():
        no_location_count = 0
        user_actions = Action.query.filter_by(user_id=user.id).filter(Action.timestamp > from_time).all()
        for action in user_actions:
            if action.location == '' or action.location == 'Неизвестно' or not action.location:
                no_location_count += 1
        if len(user_actions) == 0:
            response.append(f'{key} - нет действий')
        else:
            response.append(f'{key} - {len(user_actions) - no_location_count}/{len(user_actions)}')
    return response


def get_all_subcontractors_short_names() -> list:
    """Возвраящает все короткие названия фирм подрядчиков"""
    companies = Company.query.all()
    response = [i.org_short_name for i in companies if i.org_type == 'Подрядчик']
    return response


def get_all_valid_book_statuses() -> list:
    """Возвращает все возможные статусы книг кроме статуса '[удалено]'"""
    statuses = BookStatus.query.all()
    response = [i.status_name for i in statuses if i.status_name != '[удалено]']
    return response


def get_books_count_by_status() -> list:
    """Возвращает список с количеством книг для каждого статуса кроме статуса '[удалено]'"""
    response = []
    statuses = [i for i in BookStatus.query.all() if i.status_name != '[удалено]']
    for status in statuses:
        books_by_status = Book.query.filter_by(status_id=status.id).count()
        response.append(books_by_status)
    return response


def get_books_count_by_status_for_scs(status_name) -> list:
    """Возвращает список с количеством книг для каждого подрядчика по статусу"""
    response = []
    subcontractors = [i for i in Company.query.all() if i.org_type == 'Подрядчик']
    for sc in subcontractors:
        sc_book_count_by_status = Book.query.filter_by(
            status_id=BookStatus.query.filter_by(status_name=status_name).first().id
        ).filter(
            Book.company == sc
        ).count()
        response.append(sc_book_count_by_status)
    return response


def get_actions_in_period(time_unit, period) -> dict:
    """Формирует словарь с количеством действий за единицу
    времени на заданном промежутке от настоящего момента"""
    response = {'create': [],
                'progress': [],
                'regress': [],
                'delete': [],
                'total_actions': 0}
    today_date = date.today()
    to_time = datetime.combine(today_date, time(23, 59, 59))
    if time_unit == 'week':
        step = {'days': 7}
    elif time_unit == 'day':
        step = {'days': 1}
    else:
        cur_time = datetime.utcnow().time()
        to_time = datetime.utcnow() + timedelta(hours=1, minutes=-cur_time.minute, seconds=-cur_time.second)
        step = {'hours': 1}
    from_time = to_time - timedelta(**step)
    for i in range(period):
        create, progress, regress, delete = 0, 0, 0, 0
        actions = Action.query.filter(to_time > Action.timestamp).filter(Action.timestamp > from_time).all()
        to_time = from_time
        from_time -= timedelta(**step)
        response['total_actions'] += len(actions)
        for action in actions:
            if not action.old_status:
                create += 1
            elif action.new_status.id == BookStatus.query.all()[-1].id:
                delete -= 1
            elif action.old_status.id > action.new_status.id:
                regress += action.new_status.id - action.old_status.id
            else:
                progress += action.new_status.id - action.old_status.id
        response['create'].append(create)
        response['progress'].append(progress)
        response['regress'].append(regress)
        response['delete'].append(delete)
    response['create'].reverse()
    response['progress'].reverse()
    response['regress'].reverse()
    response['delete'].reverse()
    return response


def build_sample_db():

    import random
    import datetime
    import csv

    db.drop_all()
    db.create_all()

    # Create parent tables

    # Role table

    default_roles = [
        {'role_name': 'user'},
        {'role_name': 'manager'},
        {'role_name': 'admin'}
    ]
    roles = []
    for i in default_roles:
        i = Role(**i)
        roles.append(i)
        db.session.add(i)
    db.session.commit()
    print('Role table created')

    # Company table

    default_companies = [
        {'org_full_name': 'ООО "НИПИГАЗ"',
         'org_short_name': 'НИПИ',
         'org_type': 'ГП'},
        {'org_full_name': 'ООО "Велесстрой"',
         'org_short_name': 'ВЛС',
         'org_type': 'Подрядчик'},
        {'org_full_name': 'ООО "АСП АКВА"',
         'org_short_name': 'АКВА',
         'org_type': 'Подрядчик'},
        {'org_full_name': 'ООО "СтройСити"',
         'org_short_name': 'СС',
         'org_type': 'Подрядчик'},
        {'org_full_name': 'ООО "Урал Автоматика"',
         'org_short_name': 'УА',
         'org_type': 'Подрядчик'},
        {'org_full_name': 'ООО "Солди"',
         'org_short_name': 'СОЛДИ',
         'org_type': 'Подрядчик'},
        {'org_full_name': 'ООО "Промстрой"',
         'org_short_name': 'ПС',
         'org_type': 'Подрядчик'},
        {'org_full_name': 'ООО "Промфинстрой"',
         'org_short_name': 'ПФС',
         'org_type': 'Подрядчик'},
        {'org_full_name': 'ООО "Сервис Газификация"',
         'org_short_name': 'СГ',
         'org_type': 'СК'}
    ]
    companies = []
    for i in default_companies:
        i = Company(**i)
        companies.append(i)
        db.session.add(i)
    db.session.commit()
    print('Company table created')

    # BookStatus table

    default_statuses = [
        {'status_name': 'Формирование', 'status_duration': timedelta(days=90)},
        {'status_name': 'Проверка ГП', 'status_duration': timedelta(days=3)},
        {'status_name': 'Замечания ГП', 'status_duration': timedelta(days=90)},
        {'status_name': 'Проверка СК', 'status_duration': timedelta(days=3)},
        {'status_name': 'Замечания СК', 'status_duration': timedelta(days=90)},
        {'status_name': 'Проверка З', 'status_duration': timedelta(days=6)},
        {'status_name': 'Замечания З', 'status_duration': timedelta(days=90)},
        {'status_name': 'Архив', 'status_duration': timedelta(days=99999)},
        {'status_name': '[удалено]', 'status_duration': timedelta(days=99999)}
    ]
    statuses = []
    for i in default_statuses:
        i = BookStatus(**i)
        statuses.append(i)
        db.session.add(i)
    db.session.commit()
    print('BookStatus table created')

    # Create children tables

    # User table

    default_user = {
        'username': 'SmirnovAO',
        'company': companies[0],
        'email': 'newbox93@gmail.com',
        'telegram_id': 401814822,
        'password_hash': generate_password_hash('admin'),
        'access_role': roles[2]
    }
    users = []
    user = User(**default_user)
    users.append(user)

    names = ['Egor', 'Igor', 'Olga', 'Anna', 'Daria', 'Artur', 'Dmitri', 'Inna', 'Serega']
    for name in names:
        user = User()
        user.username = name
        user.email = name.lower() + '@test.com'
        user.telegram_id = 0
        user.password_hash = generate_password_hash('password')
        user.access_role = random.choice(roles[:2])
        user.company = random.choice(companies)
        users.append(user)
        db.session.add(user)
    db.session.commit()
    print('User table created')

    # Book table

    real_ids = []
    with open('real_id_set.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            real_ids.append(row[0])
    for i in range(1, 256):
        qr_id = 'AGPZ-' + '0' * (6 - len(str(i))) + str(i)
        real_id = real_ids[i]
        status = statuses[0]
        company = random.choice(companies[1:len(companies)-1])
        user = users[0]
        tmp = random.randint(30, 50)
        timestamp = datetime.datetime.now() - datetime.timedelta(days=tmp)
        book = Book(qr_id=qr_id,
                    real_id=real_id,
                    book_status=status,
                    company=company)
        db.session.add(book)
        db.session.commit()
        action = Action(action=f'{status.status_name} (Создание)',
                        author=user,
                        book=book,
                        timestamp=timestamp,
                        location='Неизвестно',
                        new_status=status)
        db.session.add(action)
        db.session.commit()
    print('Book table created')

    # Action table

    for i in range(1, 500):
        book = Book.query.get(random.randint(1, 255))
        old_status = book.status_id
        if old_status == 9:
            continue
        new_status = statuses[old_status]
        user = random.choice(users)
        old_status = book.book_status
        tmp = random.randint(1, 30)
        timestamp = datetime.datetime.now() - datetime.timedelta(days=tmp)
        book.book_status = new_status
        action = Action(action=f'{old_status.status_name} -> {new_status.status_name}',
                        author=user,
                        book=book,
                        timestamp=timestamp,
                        location='Неизвестно',
                        old_status=old_status,
                        new_status=new_status
                        )
        db.session.add(action)
        db.session.commit()
    print('Action table created')
    db.session.commit()
