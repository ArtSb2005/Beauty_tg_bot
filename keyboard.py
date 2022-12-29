import datetime
from datetime import datetime
from calendar import monthrange
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from datetime import date
from main import db


def start_keyboard():
    Menu = InlineKeyboardMarkup(row_width=2)
    inline_btn_1 = InlineKeyboardButton('Записаться', callback_data='inline_btn_sign')
    inline_btn_2 = InlineKeyboardButton('Проверить мою запись', callback_data='inline_btn_check_sign')
    inline_btn_3 = InlineKeyboardButton('Отменить запись', callback_data='inline_btn_del_sign')
    inline_btn_4 = InlineKeyboardButton('Часто задаваемые вопросы (FAQ)', callback_data='inline_btn_faq')
    Menu.insert(inline_btn_1)
    Menu.insert(inline_btn_2)
    Menu.insert(inline_btn_3)
    Menu.insert(inline_btn_4)
    return Menu

def record_keyboard():
    Menu = InlineKeyboardMarkup(row_width=2)
    for i in db.get_services():
        Menu.insert(InlineKeyboardButton(i[1], callback_data=f'inline_btn_services_{i[0]}'))
    return Menu

def mounth_keyboard():
    Menu = InlineKeyboardMarkup(row_width=2)
    data = str(date.today()).split("-")
    list_data = {'01':'Январь', '02':'Февраль', '03':'Март', '04':'Апрель',
                 '05':'Май', '06':'Июнь', '07':'Июль', '08':'Август', '09':'Сентябрь', '10':'Октябрь',
                 '11':'Ноябрь', '12':'Декабрь'}
    for a,b in list_data.items():
        Menu.insert(InlineKeyboardButton(b, callback_data=f'inline_btn_mounth_{a}'))
    Menu.insert(InlineKeyboardButton("Стоп", callback_data=f'inline_btn_mounth_stop'))
    return Menu


def time_keyboard(mounth, data):
    Menu = InlineKeyboardMarkup(row_width=2)
    list_time_records = []
    mn = {}
    dat = str(date.today()).split("-")
    new_data = ''

    if len(data) < 2:
        new_data += '0' + str(data)
    else:
        new_data += data

    for i in db.get_all_records():
        data_rec = i[-1].split("-")
        #mounth           #date
        mn[data_rec[0]] = f"{data_rec[1]}-{i[-2]}"


    for a,b in mn.items():
        nt = b.split('-')
        if a == mounth and nt[0] == new_data:
            for i in db.get_time_records():
                if nt[1] != i[1]:
                    list_time_records.append(i[0])

    for a in db.get_time():
        if a[1] in list_time_records:
            pass
        else:
            Menu.insert(InlineKeyboardButton(a[1], callback_data=f'inline_btn_time_{a[0]}'))

    Menu.insert(InlineKeyboardButton("Стоп", callback_data=f'inline_btn_time_stop'))
    return Menu

def date_keyboard(data):
    Menu = InlineKeyboardMarkup(row_width=2)
    today = int(str(date.today()).split("-")[-1])+1
    mounth = int(str(date.today()).split("-")[1])

    current_year = datetime.now().year
    month = int(data)
    days = monthrange(current_year, month)[1]

    if mounth == int(data):
        for i in range(today, days+1):
            Menu.insert(InlineKeyboardButton(str(today) + " числа", callback_data=f'inline_btn_time_{today}'))
            today += 1
    else:
        for i in range(1, days+1):
            Menu.insert(InlineKeyboardButton(str(i) + " числа", callback_data=f'inline_btn_time_{i}'))
    Menu.insert(InlineKeyboardButton("Стоп", callback_data=f'inline_btn_time_stop'))
    return Menu

def del_records(user):
    Menu = InlineKeyboardMarkup(row_width=1)
    for i in db.get_records(user):
        data = i[-1].split('-')
        Menu.insert(InlineKeyboardButton(f"{i[4]} {data[1]}-{data[0]} в {i[-2]}", callback_data=f'inline_btn_delete_{i[0]}'))
    return Menu


