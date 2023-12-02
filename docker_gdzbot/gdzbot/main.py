from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
import psycopg2
from psycopg2.extras import DictCursor
from gdz_user import GDZUser
import asyncio
import logging
import sys
from gdz_keyboards import Keyboards
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from text_samples import TextSamples
from TGAdapters import GptAdaper, Helper

from creds import gdz_bot_token, gdz_gpt_token, DBConnectParams
dp = Dispatcher()
bot = Bot(token=gdz_bot_token, parse_mode=ParseMode.HTML)
keyboards = Keyboards()
ts = TextSamples()

gdz_users = {}
chats = {}
main_router = Router()

gpt = GptAdaper()
hp = Helper()

class GptWritting(StatesGroup):
    accept_request = State()
    writing = State()
    


async def get_data_for_user():
    with psycopg2.connect(**DBConnectParams, cursor_factory=DictCursor) as connection:
        with connection.cursor() as cursor:
            cursor.execute()

async def save_data_for_user(telegram_id, chat_id, username, phone=None):
    with psycopg2.connect(**DBConnectParams, cursor_factory=DictCursor) as connection:
        with connection.cursor() as cursor:
            values_to_insert = {'telegram_id':telegram_id,
                                'chat_id':chat_id,
                                'username':username}
            columns = ', '.join(values_to_insert.keys())
            placeholders = ', '.join(['%s'] * len(values_to_insert))
            query = f'INSERT INTO accounts_bot ({columns}) VALUES ({placeholders})'
            cursor.execute(query, tuple(values_to_insert.values()))
            connection.commit()

@dp.message(CommandStart())
async def start_command_handler(message: Message) -> None:
    try:
       await bot.delete_message(chat_id = message.chat.id,
                                     message_id=chats[message.chat.id])
    except:
        pass

    await keyboards.create_keyboards()
    await save_data_for_user(telegram_id=message.from_user.id,username=message.from_user.username,chat_id=message.chat.id)
    new_message = await message.answer('Выбери, что тебе нужно 👇', reply_markup=keyboards.main)
    chats[message.chat.id] = new_message.message_id
    gdz_users[message.from_user.id] = GDZUser()
    gdz_users[message.from_user.id].telegram_id = message.from_user.id
    gdz_users[message.from_user.id].username = message.from_user.username
    gdz_users[message.from_user.id].chat_id = message.chat.id


@dp.callback_query(lambda call: call.data == 'free_writting')
async def free_writing_menu_handler(call: CallbackQuery) -> None:
    try: 
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                     message_id=chats[call.message.chat.id], 
                                     text='Выбери, что тебе нужно 👇',
                                    reply_markup=keyboards.free_writting)
    except:
        new_message = await bot.send_message(chat_id=call.message.chat.id,text='Выбери, что тебе нужно 👇', reply_markup=keyboards.free_writting)
        chats[call.message.chat.id] = new_message.message_id

@dp.callback_query(lambda call: call.data == 'сomposition')
async def composition_handler(call: CallbackQuery, state: FSMContext) -> None:
    try:
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                        message_id=chats[call.message.chat.id], 
                                        text=ts.composition_text)
    except:
        new_message = await bot.send_message(chat_id=call.message.chat.id,text=ts.composition_text)
        chats[call.message.chat.id] = new_message.message_id
    await state.set_state(GptWritting.accept_request)

@main_router.message(GptWritting.accept_request)
async def gpt_request(message: Message, state: FSMContext) -> None:
    await state.set_state(GptWritting.writing)
    try:
        gpt_output = await gpt.easy_gpt(token=gdz_gpt_token,input=message.text)
    except:
        gpt_output = ['Ответ не был получен']
    current_answer = {'role': 'assistant',
                        'content': f"{gpt_output}"}
    if '⚠️ Непредвиденная ошибка' in gpt_output:
        new_message = await bot.send_message(chat_id=1198816769, text=f'⚠️ Непредвиденная ошибка ⚠️\Попробуйте снова!')
        chats[message.chat.id] = new_message.message_id
    else:
        new_message = await bot.send_message(text=f'{gpt_output}',chat_id=message.chat.id)
        chats[message.chat.id] = new_message.message_id
    await state.clear()

@dp.callback_query()
async def composition(callback: CallbackQuery) -> None:
    await callback.answer()

async def main() -> None:
    dp.include_router(main_router)
    await dp.start_polling(bot, skip_updates=True)
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())