# -*- coding: utf-8 -*-
#!venv/bin/python
import asyncio
import aioschedule
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from db import Database
from keyboard import *

class AddRecord(StatesGroup):
    name = State()
    mounth = State()
    date = State()
    time = State()
    user_name = State()
    phone = State()


bot = Bot(token="5669065628:AAHP3ClyiBzxTmnYU_0LUqSI5ZzI4luB9Co") # Ваш токен бота
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
db = Database('database.db')

@dp.message_handler(commands="start") # Функция, которая будет вызываться при команде /start
async def cmd_start(message: types.Message):
    start_button = ReplyKeyboardMarkup()
    start_button.add(KeyboardButton("Записаться"), KeyboardButton("Проверить мою запись"), KeyboardButton("Отменить запись"), KeyboardButton("Часто задаваемые вопросы (FAQ)"))
    await message.answer("Вас приветствует бот по записи.", reply_markup=start_button)

@dp.message_handler(lambda message: message.text == "Записаться") #Функция, которая будет вызываться при нажатии на кнопку "Записаться"
async def set_records(message: types.Message):
    await message.answer("Выберите услугу:", reply_markup=record_keyboard())
    await AddRecord.name.set()

@dp.callback_query_handler(state=AddRecord.name) # Функция, которая будет вызываться при нажатии на кнопку с названием услуги
async def set_username(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data[-4:] == 'stop':
        await state.finish()
        await bot.send_message(callback_query.from_user.id, f"Вы вышли из записи")
    else:
        for i in db.get_services():
            if i[0] == int(callback_query.data[-1]):
                await state.update_data(name=i[1])
                await AddRecord.mounth.set()
                await bot.send_message(callback_query.from_user.id, "Выберите месяц:", reply_markup=mounth_keyboard())

@dp.callback_query_handler(state=AddRecord.mounth) # Функция, которая будет вызываться при нажатии на кнопку с названием месяца
async def set_date(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data[-4:] == 'stop':
        await state.finish()
        await bot.send_message(callback_query.from_user.id, f"Вы вышли из записи")
    else:
        date = callback_query.data.split("_")
        await state.update_data(mounth=date[-1])
        data = await state.get_data()
        await bot.send_message(callback_query.from_user.id, f"Выберите дату:", reply_markup=date_keyboard(data['mounth']))
        await AddRecord.date.set()

@dp.callback_query_handler(state=AddRecord.date) # Функция, которая будет вызываться при нажатии на кнопку с названием даты
async def set_date(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data[-4:] == 'stop':
        await state.finish()
        await bot.send_message(callback_query.from_user.id, f"Вы вышли из записи")
    else:
        date = callback_query.data.split("_")
        await state.update_data(date=date[-1])
        data = await state.get_data()
        await bot.send_message(callback_query.from_user.id, f"Выберите время:", reply_markup=time_keyboard(data['mounth'], date[-1]))
        await AddRecord.time.set()


@dp.callback_query_handler(state=AddRecord.time) # Функция, которая будет вызываться при нажатии на кнопку с названием времени
async def set_time(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data[-4:] == 'stop':
        await state.finish()
        await bot.send_message(callback_query.from_user.id, f"Вы вышли из записи")
    else:
        for i in db.get_time():
            if i[0] == int(callback_query.data[-1]):
                await state.update_data(time=i[1])
                await bot.send_message(callback_query.from_user.id, f"Введите своё имя.")
                await AddRecord.user_name.set()

@dp.message_handler(state=AddRecord.user_name) # Функция, которая будет вызываться при вводе имени
async def set_username(message: types.Message, state: FSMContext):
    if message.text == 'Стоп':
        await state.finish()
        await message.answer("Вы вышли из записи")
    else:
        await state.update_data(user_name=message.text)
        await message.answer(f"Введите свой номер телефона.")
        await AddRecord.phone.set()

@dp.message_handler(state=AddRecord.phone) # Функция, которая будет вызываться при вводе номера телефона
async def set_phone(message: types.Message, state: FSMContext):
    if message.text == '/stop':
        await state.finish()
        await message.answer("Вы вышли из записи")
    else:
        await state.update_data(phone=message.text)
        data = await state.get_data()
        db.add_user_records(message.from_user.id, data['name'], data['time'], data['user_name'], data['phone'],
                            f"{data['mounth']}-{data['date']}")
        await message.answer(f"Вы записаны на {data['name']} в {data['time']}")
        await state.finish()


@dp.message_handler(lambda message: message.text == "Проверить мою запись") # Функция, которая будет вызываться при нажатии на кнопку "Проверить мою запись"
async def check_records(message: types.Message):
    text = ''
    records = db.get_records(message.from_user.id)
    for i in records:
        data = i[-1].split('-')
        text += f"\n{i[4]} {data[1]}-{data[0]} в {i[-2]}"
    await message.answer("Ваши записи:\n"+text)

@dp.message_handler(lambda message: message.text == "Отменить запись") # Функция, которая будет вызываться при нажатии на кнопку "Отменить запись"
async def del_records_ch(message: types.Message):
    await message.answer("Выберите запись для удаления:", reply_markup=del_records(message.from_user.id))

@dp.callback_query_handler(text_contains="inline_btn_delete_") # Функция, которая будет вызываться при нажатии на кнопку "Удалить запись"
async def del_records_del(callback_query: types.CallbackQuery):
    records = callback_query.data.split("_")[-1]
    db.delete_records(records)
    await bot.send_message(callback_query.from_user.id, f"Запись удалена")

@dp.message_handler(lambda message: message.text == "Часто задаваемые вопросы (FAQ)") # Функция, которая будет вызываться при нажатии на кнопку "Часто задаваемые вопросы (FAQ)"
async def faq(message: types.Message):
    await message.answer("Часто задаваемые вопросы (FAQ)")

@dp.message_handler(commands="admin") # Функция, которая будет вызываться при нажатии на команду "/admin"
async def adm(message: types.Message):
    inline_btn_1 = InlineKeyboardButton("Вывести все записи", callback_data='all_records')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
    await message.answer("Админ панель", reply_markup=inline_kb1)

@dp.callback_query_handler(lambda c: c.data == 'all_records') # Функция, которая будет вызываться при нажатии на кнопку "Вывести все записи"
async def all_records(callback_query: types.CallbackQuery):
    text = ''
    records = db.get_all_records()
    for i in records:
        data = i[-1].split('-')
        text += f"\n{i[4]} {data[1]}-{data[0]} в {i[-2]}. Имя/номер: {i[1]}/{i[3]}"
    await bot.send_message(callback_query.from_user.id, "Все записи:\n" + text)

@dp.message_handler()
async def choose_your_dinner():
    today = str(date.today()).split("-")
    for user in db.get_all_records():
        data = user[-1].split('-')
        if int(data[-1]) == int(today[-1])+1 and int(data[0]) == int(today[1]):
            await bot.send_message(chat_id =user[2], text = f"Вы записаны завтра на {user[4]}.")
        else:
            if int(data[-1]) == int(today[-1]) and int(data[0]) == int(today[1]):
                db.delete_records(user[0])


async def scheduler(): # Функция, которая будет вызываться каждый день в 10:00
    aioschedule.every().day.at("10:00").do(choose_your_dinner)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(dp):
    asyncio.create_task(scheduler())

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)