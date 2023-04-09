import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor


logging.basicConfig(level=logging.INFO)


TOKEN = "5889925546:AAGHN-TOJHhXXe4fu_QAn0oaNll7inOENVI"
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

connection = sqlite3.connect('data.db')
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        telegram_name TEXT NOT NULL,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
""")


class RegistrationForm(StatesGroup):
    name = State()
    age = State()
    telegram_name = State()
    login = State()
    password = State()
    cancel = State()


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    registration_button = types.KeyboardButton(text="Registration")
    keyboard.row(registration_button)

    await message.answer(
        "Hello! If the bot will not work, type the command /start. \nNow please select the option:",
        reply_markup=keyboard
    )


@dp.message_handler(Text(equals="Cancel"), state=RegistrationForm)
async def cancel_registration(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Registration cancelled. Please start a new registration.")
    await registration_handler(message)

@dp.message_handler(Text(equals="Registration"))
async def registration_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = types.KeyboardButton(text="Cancel")
    keyboard.add(cancel_button)

    await message.answer(
        "Please provide your information.\n"
        "What is your name?",
        reply_markup=keyboard
    )
    await RegistrationForm.name.set()


@dp.message_handler(state=RegistrationForm.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    if len(name) < 2:
        await message.answer("Please enter a valid name. It should be at least 2 characters long.")
        return
    await state.update_data(name=name)
    await message.answer("What is your age?")
    await RegistrationForm.next()


@dp.message_handler(state=RegistrationForm.age, content_types=types.ContentTypes.TEXT)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    if not age.isnumeric():
        await message.answer("Please enter a valid age. It should be a number.")
        return
    await state.update_data(age=age)
    await message.answer("What is your telegram name?")
    await RegistrationForm.next()

@dp.message_handler(state=RegistrationForm.telegram_name, content_types=types.ContentTypes.TEXT)
async def process_telegram_name(message: types.Message, state: FSMContext):
    telegram_name = message.text
    if str(telegram_name)[0] != "@":
        await message.answer("start your nickname in the telegram with @")
        return
    await state.update_data(telegram_name=telegram_name)
    await message.answer("What is your login?")
    await RegistrationForm.next()


@dp.message_handler(state=RegistrationForm.login)
async def process_login(message: types.Message, state: FSMContext):
    login = message.text
    if len(login) < 3:
        await message.answer("Please enter a valid login. It should be at least 3 characters long.")
        return

    # Check if the login already exists in the database
    cursor.execute("SELECT login FROM users WHERE login=?", (login,))
    result = cursor.fetchone()
    if result is not None:
        await message.answer("This login is already taken. Please choose another one.")
        return

    await state.update_data(login=login)
    await message.answer("What is your password? At least 6 charachters)")
    await RegistrationForm.next()


@dp.message_handler(state=RegistrationForm.password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    if len(password) < 6:
        await message.answer("Please enter a valid password. It should be at least 6 characters long.")
        return

    # Get data from state
    async with state.proxy() as data:
        name = data['name']
        age = data['age']
        telegram_name = data['telegram_name']
        login = data['login']

    # Save data to SQLite database
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    cursor.execute("INSERT INTO users (name, age, telegram_name, login, password) VALUES (?, ?, ?, ?, ?)",
                   (name, age, telegram_name, login, password))
    connection.commit()
    connection.close()

    await message.answer("Thank you for registering!\n\n"
                          f"Name: {name}\n"
                          f"Age: {age}\n"
                          f"telegram_name {telegram_name}\n"
                          f"Login: {login}\n"
                          f"Password: {password}",
                          parse_mode=ParseMode.HTML)
    await state.finish()

    await registration_handler(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

