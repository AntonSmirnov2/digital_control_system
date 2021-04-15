import os
import re

from PIL import Image
import cv2
from pyzbar.pyzbar import decode
from jinja2 import Template

from app import bot
from app.plugins.db_helpers import get_book_status_and_real_id
from app.plugins.bot_markups import change_book_status_markup


def decrypt_photo():
    """Пытается распознать QR-код на фото и формирует текст ответа и inline-клавиатуру
    в зависимости от результата расшифровки"""
    markup = None

    photo_content = decrypt_qr_code()
    os.remove(r'bot_tmp_files\qrcode.jpg')
    if not photo_content:
        reply_text = 'Код не распознан.'
        return reply_text, markup
    qr_id = filter_decrypted_content(photo_content)
    if not qr_id:
        reply_text = f'Содержиме QR-кода:\n{photo_content}\n\nФормат для доступа к БД: AGPZ-123456.'
        return reply_text, markup
    book_status, book_id = get_book_status_and_real_id(qr_id)
    if not book_status:
        reply_text = f'{qr_id}.\n\nДанный QR-код не зарегистрирован в системе.'
    else:
        reply_text = f'{book_id}\n\nИзменение статуса:'
        markup = change_book_status_markup(book_status, qr_id)
    return reply_text, markup


def download_photo(message):
    """Скачивает и сохраняет присланное фото"""
    file_id = message.photo[-1].file_id
    photo = bot.get_file(file_id)
    downloaded_photo = bot.download_file(photo.file_path)
    with open(r"bot_tmp_files\qrcode.jpg", 'wb') as new_file:
        new_file.write(downloaded_photo)


def render_html_for_tg(html_name, **kwargs):
    template_path = os.path.join(r'app\templates\bot', html_name)
    with open(template_path, 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        return template.render(**kwargs)


def callback_to_dict(callback_body: str):
    answer = callback_body.split('&')
    answer = {i.split('=')[0]: i.split('=')[1] for i in answer if i}
    return answer


def filter_decrypted_content(qr_content: str):
    """Находит строку вида AGPZ-123456 в расшифрованном тексте с QR-кода"""

    pattern = r'\b\w{4}-\d{6}\b'
    result = re.match(pattern, qr_content)
    if result:
        return result.group(0)


def _decrypt_pyzbar(path=r'bot_tmp_files\qrcode.jpg'):
    im = Image.open(path)
    qr_content = decode(im)
    if qr_content:
        return qr_content[0][0].decode('utf-8')


def _decrypt_cv2(path=r'bot_tmp_files\qrcode.jpg'):
    img = cv2.imread(path)
    detector = cv2.QRCodeDetector()
    qr_content = detector.detectAndDecodeMulti(img)
    if qr_content[0]:
        return qr_content[1][0]


def decrypt_qr_code(path=r'bot_tmp_files\qrcode.jpg'):
    return _decrypt_pyzbar(path) or _decrypt_cv2(path)

