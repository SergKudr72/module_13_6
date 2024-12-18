from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = "7612810185:AAF3uy1raG1EH2x8bLwhZbAs7lskd_kW6ZU"  # "???token_bot???"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
kb.row(button1, button2)

kb_call = InlineKeyboardMarkup()
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_call.add(button3, button4)


class UserState(StatesGroup):
    gender = State()
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=kb)


@dp.message_handler(text="Информация")
async def info_message(message):
    await message.answer("Данный бот создан для помощи в расчете необходимого количества килокалорий в сутки "
                         "для каждого конкретного человека по формуле Миффлина-Сан Жеора")


@dp.message_handler(text="Рассчитать")
async def main_gender(message):
    await message.answer("Введите свой пол (мужской или женский):")
    await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def fsm_send_menu(message, state):
    await state.update_data(first_gender=message.text)
    await message.answer("Выберите опцию:", reply_markup=kb_call)


@dp.callback_query_handler(state=UserState.gender, text='formulas')
async def get_formulas(call, state):
    data = await state.get_data()
    if str(data['first_gender']) == "мужской":
        await call.message.answer("10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) + 5")
        await call.answer()
    else: # elif str(data['first_gender']) == "женский":
        await call.message.answer("10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161")
        await call.answer()
    # else:
    #     await call.message.answer('Введены некорректные данные по полу.')
    #     await call.answer()


@dp.callback_query_handler(state=UserState.gender, text='calories')
async def set_age(call, state):
    data = await state.get_data()
    if str(data['first_gender']) == "мужской":
        await call.message.answer('Введите свой возраст (лет):')
        await UserState.age.set()
        await call.answer()
    else:
        await call.message.answer('Введите свой возраст (лет):')
        await UserState.age.set()
        await call.answer()


@dp.message_handler(state=UserState.age)
async def fsm_set_growth(message, state):
    try:
        await state.update_data(first_age=int(message.text))
        await UserState.growth.set()
        await message.answer('Введите свой рост (см):')
    except ValueError:
        await message.answer('Введены некорректные данные по возрасту.')


@dp.message_handler(state=UserState.growth)
async def fsm_set_weight(message, state):
    try:
        await state.update_data(first_growth=int(message.text))
        await UserState.weight.set()
        await message.answer('Введите свой вес (кг):')
    except ValueError:
        await message.answer('Введены некорректные данные по росту.')


@dp.message_handler(state=UserState.weight)
async def fsm_send_calories(message, state):
    try:
        await state.update_data(first_weight=int(message.text))
        data = await state.get_data()
        if str(data['first_gender']) == "мужской":
            result_m = round(
                10 * int(data['first_weight']) + 6.25 * int(data['first_growth']) - 5 * int(data['first_age']) + 5, 2)
            await message.answer(f'Ваша норма калорий для мужчин: {result_m} ккал')
            await state.finish()
        else:
            result_w = round(
                10 * int(data['first_weight']) + 6.25 * int(data['first_growth']) - 5 * int(data['first_age']) - 161, 2)
            await message.answer(f'Ваша норма калорий для женщин: {result_w} ккал')
            await state.finish()
    except ValueError:
        await message.answer('Введены некорректные данные по весу.')


@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
