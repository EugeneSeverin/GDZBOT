from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import input_file, Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
import asyncpg
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
from aiogram.types import URLInputFile,BufferedInputFile, FSInputFile
from datetime import datetime
import os

from creds import gdz_bot_token, gdz_gpt_token, DBConnectParams
dp = Dispatcher()
bot = Bot(token=gdz_bot_token, parse_mode=ParseMode.HTML)
keyboards = Keyboards()
ts = TextSamples()

gdz_users = {}
chats = {}
main_router = Router()

gpt = GptAdaper(token=gdz_gpt_token)
hp = Helper()

class GptWritting(StatesGroup):
    accept_request = State()
    writing = State()

class GptPhoto(StatesGroup):
    accept_photo = State()
    finish_photo = State()

request_samples_writting_messages = {'сomposition': {'text':ts.composition_text,'gpt_prompt':'Сочинение'},
                        'essay': {'text':ts.essay,'gpt_prompt':'Эссе'},
                        'free_message': {'text':ts.free_message,'gpt_prompt':'Напиши сообщение на тему'},
                        'abstract': {'text':ts.abstract,'gpt_prompt':'Реферат'},
                        'report':{'text':ts.report,'gpt_prompt':'Доклад'},
                        'exposition':{'text':ts.exposition,'gpt_prompt':'Кратко изложи текст'},
                        'other_writting':{'text':ts.other_writting,'gpt_prompt':''}}
request_samples_writting_callback_list = list(request_samples_writting_messages.keys())




async def get_data_for_users():
    connection = await asyncpg.connect(**DBConnectParams)
    data = await connection.fetch("SELECT * FROM accounts_bot")
    for row in data:
        user = GDZUser()
        user.telegram_id = row['telegram_id']
        user.chat_id = row['chat_id']
        user.username = row['username']
        user.credit = row['credit']
        user.request_limit = row['request_limit']
        user.requests_today = row['requests_today']
        user.access_level = row['access_level']
        user.gdz_id = row['gdz_id']
        gdz_users[user.telegram_id] = user
    await connection.close()

async def save_data_for_user(telegram_id, chat_id, username, phone=None):
    async with asyncpg.create_pool(**DBConnectParams) as pool:
        async with pool.acquire() as connection:
            values_to_insert = (telegram_id, chat_id, username)
            columns = 'telegram_id, chat_id, username'
            if phone is not None:
                columns += ', phone'
                values_to_insert += (phone,)
            placeholders = ', '.join('$' + str(i) for i in range(1, len(values_to_insert) + 1))
            query = f'INSERT INTO accounts_bot ({columns}) VALUES ({placeholders})'
            await connection.execute(query, *values_to_insert)


async def subtruck_genshins(telegram_id, credit):
    async with asyncpg.create_pool(**DBConnectParams) as pool:
        async with pool.acquire() as connection:
            values_to_update = {'credit':credit,
                      'telegram_id':telegram_id}
            query = f"""UPDATE accounts_bot SET credit=$1 WHERE telegram_id=$2;"""
            await connection.execute(query, *values_to_update.values())

async def create_userdir(telegram_id):
    if not os.path.exists(f'/users/{str(telegram_id)}'):
        os.makedirs(f'/users/{telegram_id}')
        print('111')

@dp.message(CommandStart())
async def start_command_handler(message: Message) -> None:
    try:
       await bot.delete_message(chat_id = message.chat.id,
                                     message_id=chats[message.chat.id])
    except:
        pass
    if gdz_users.get(message.from_user.id) is None:
        await save_data_for_user(telegram_id=message.from_user.id,username=message.from_user.username,chat_id=message.chat.id)
        await create_userdir(telegram_id=message.from_user.id)
        new_message = await bot.send_message(chat_id=message.chat.id, text='Выбери, что тебе нужно 👇', reply_markup=keyboards.main)
        chats[message.chat.id] = new_message.message_id
        gdz_users[message.from_user.id] = GDZUser()
        gdz_users[message.from_user.id].telegram_id = message.from_user.id
        gdz_users[message.from_user.id].username = message.from_user.username
        gdz_users[message.from_user.id].chat_id = message.chat.id
    else:
        new_message = await bot.send_message(chat_id=message.chat.id, text='Выбери, что тебе нужно 👇', reply_markup=keyboards.main)
        chats[message.chat.id] = new_message.message_id



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

@dp.callback_query(lambda call: call.data in request_samples_writting_callback_list)
async def composition_handler(call: CallbackQuery, state: FSMContext) -> None:
    text = request_samples_writting_messages[call.data]['text']
    gdz_users[call.from_user.id].requested_theme = request_samples_writting_messages[call.data]['gpt_prompt']
    try:
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                        message_id=chats[call.message.chat.id], 
                                        text=text)
    except:
        new_message = await bot.send_message(chat_id=call.message.chat.id,text=ts.composition_text)
        chats[call.message.chat.id] = new_message.message_id
    await state.set_state(GptWritting.accept_request)

# =======================================================================================
# ===================================== PHOTO ===========================================
# =======================================================================================

@dp.callback_query(lambda call: call.data == 'photo_analysis')
async def free_writing_menu_handler(call: CallbackQuery, state: FSMContext) -> None:
    try: 
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                     message_id=chats[call.message.chat.id], 
                                     text='Отправь в чат любое фото',
                                    reply_markup=keyboards.back_to_main_menu)
    except:
        new_message = await bot.send_message(chat_id=call.message.chat.id,text='Отправь в чат любое фото', reply_markup=keyboards.back_to_main_menu)
        chats[call.message.chat.id] = new_message.message_id
    await state.set_state(GptPhoto.accept_photo)

@dp.callback_query(lambda call: call.data in request_samples_writting_callback_list)
async def composition_handler(call: CallbackQuery, state: FSMContext) -> None:
    text = request_samples_writting_messages[call.data]['text']
    gdz_users[call.from_user.id].requested_theme = request_samples_writting_messages[call.data]['gpt_prompt']
    try:
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                        message_id=chats[call.message.chat.id], 
                                        text=text)
    except:
        new_message = await bot.send_message(chat_id=call.message.chat.id,text=ts.composition_text)
        chats[call.message.chat.id] = new_message.message_id
    await state.set_state(GptWritting.accept_request)

@main_router.message(GptPhoto.accept_photo)
async def handle_photo(message: Message, state: FSMContext) -> None:
    await state.set_state(GptPhoto.finish_photo)
    photo = message.photo[-1]
    buf_file = FSInputFile(photo)
    await bot.send_photo(photo=buf_file, caption='Посмотри на эту фотографию 🔥', chat_id=message.chat.id)

#     try:
#         input_text = gdz_users[message.from_user.id].requested_theme + " " + message.text
#         gpt_output = await gpt.easy_gpt(token=gdz_gpt_token,input=input_text)
#     except:
#         gpt_output = ['Ответ не был получен']
#     current_answer = {'role': 'assistant',
#                         'content': f"{gpt_output}"}
#     if '⚠️ Непредвиденная ошибка' in gpt_output:
#         new_message = await bot.send_message(chat_id=1198816769, text=f'⚠️ Непредвиденная ошибка у юзера {message.from_user.id} ⚠️\Попробуйте снова!')
#         new_message = await bot.send_message(chat_id=message.chat.id, text=f'⚠️ Непредвиденная ошибка ⚠️\Попробуйте снова!')
#     elif gdz_users[message.from_user.id].credit < 5:
#         new_message = await bot.send_message(chat_id=message.chat.id, text=f'Недостаточно геншинов ❌\nПодождите до завтра или пополните счет.',reply_markup=keyboards.back_to_main_menu)
#         chats[message.chat.id] = new_message.message_id
#         gdz_users[message.from_user.id].gpt_reply = 'Недостаточно геншинов ❌\nПодождите до завтра или пополните счет.'
#     else:
#         new_message = await bot.send_message(text=f'{gpt_output}',chat_id=message.chat.id, reply_markup=keyboards.back_to_main_menu)
#         chats[message.chat.id] = new_message.message_id
#         gdz_users[message.from_user.id].gpt_reply = gpt_output
#         gdz_users[message.from_user.id].credit -= 5
#         await subtruck_genshins(telegram_id=message.from_user.id, credit=gdz_users[message.from_user.id].credit)
#     await state.clear()










@dp.callback_query(lambda call: call.data == 'user_profile')
async def my_profile_handler(call: CallbackQuery) -> None:
    profile_sample = f"""Данные профиля:\nВаш ID: {gdz_users[call.from_user.id].gdz_id}\nPremium: ❌\nТекущий баланс геншинов: {gdz_users[call.from_user.id].credit}\nПлатный остаток геншинов: 0\nБесплатные геншины обновляются ежедневно!"""
    gdz_users[call.from_user.id].gdz_id
    try: 
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                     message_id=chats[call.message.chat.id], 
                                     text=profile_sample,
                                    reply_markup=keyboards.back_to_main_menu)
    except:
        new_message = await bot.send_message(chat_id=call.message.chat.id,text=profile_sample, reply_markup=keyboards.back_to_main_menu)
        chats[call.message.chat.id] = new_message.message_id

@dp.callback_query(lambda call: call.data == 'about_bot')
async def about_bot_handler(call: CallbackQuery) -> None:
    profile_sample = f"""О боте\nСегодня: <b>{datetime.today().now().strftime("%m/%d/%Y, %H:%M:%S")}</b>\nКоличество пользователей:<b> {len(gdz_users)}</b>\n"""
    gdz_users[call.from_user.id].gdz_id
    try: 
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                     message_id=chats[call.message.chat.id], 
                                     text=profile_sample,
                                    reply_markup=keyboards.back_to_main_menu)
    except:
        new_message = await bot.send_message(chat_id=call.message.chat.id,text=profile_sample, reply_markup=keyboards.back_to_main_menu)
        chats[call.message.chat.id] = new_message.message_id


@dp.callback_query(lambda call: call.data == 'back_to_main_menu')
async def back_to_main_menu_handler(call: CallbackQuery) -> None:
    if gdz_users[call.from_user.id].gpt_reply != None:
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                     message_id=chats[call.message.chat.id],
                                     text=gdz_users[call.from_user.id].gpt_reply)
        new_message = await bot.send_message(chat_id=call.message.chat.id, text='Выбери, что тебе нужно 👇', reply_markup=keyboards.main)
        chats[call.message.chat.id] = new_message.message_id
        gdz_users[call.from_user.id].gpt_reply = None
    else:
        try:
            await bot.edit_message_text(chat_id = call.message.chat.id,
                                         message_id=chats[call.message.chat.id],
                                         text='Выбери, что тебе нужно 👇',
                                         reply_markup=keyboards.main)
        except:
            await bot.send_message(chat_id = call.message.chat.id,
                                         message_id=chats[call.message.chat.id],
                                         text='Выбери, что тебе нужно 👇',
                                         reply_markup=keyboards.main)
            chats[call.message.chat.id] = new_message.message_id

#async def message_to_all_users():
#    for user in gdz_users.values():
#        image = URLInputFile(
#                            "https://disgustingmen.com/wp-content/uploads/2020/05/4.jpg")
#        await bot.send_photo(photo=image, caption='Посмотри на эту фотографию 🔥', chat_id=user.chat_id)

@main_router.message(GptWritting.accept_request)
async def gpt_request(message: Message, state: FSMContext) -> None:
    await state.set_state(GptWritting.writing)
    try:
        input_text = gdz_users[message.from_user.id].requested_theme + " " + message.text
        gpt_output = await gpt.easy_gpt(token=gdz_gpt_token,input=input_text)
    except:
        gpt_output = ['Ответ не был получен']
    current_answer = {'role': 'assistant',
                        'content': f"{gpt_output}"}
    if '⚠️ Непредвиденная ошибка' in gpt_output:
        new_message = await bot.send_message(chat_id=1198816769, text=f'⚠️ Непредвиденная ошибка у юзера {message.from_user.id} ⚠️\Попробуйте снова!')
        new_message = await bot.send_message(chat_id=message.chat.id, text=f'⚠️ Непредвиденная ошибка ⚠️\Попробуйте снова!')
    elif gdz_users[message.from_user.id].credit < 5:
        new_message = await bot.send_message(chat_id=message.chat.id, text=f'Недостаточно геншинов ❌\nПодождите до завтра или пополните счет.',reply_markup=keyboards.back_to_main_menu)
        chats[message.chat.id] = new_message.message_id
        gdz_users[message.from_user.id].gpt_reply = 'Недостаточно геншинов ❌\nПодождите до завтра или пополните счет.'
    else:
        new_message = await bot.send_message(text=f'{gpt_output}',chat_id=message.chat.id, reply_markup=keyboards.back_to_main_menu)
        chats[message.chat.id] = new_message.message_id
        gdz_users[message.from_user.id].gpt_reply = gpt_output
        gdz_users[message.from_user.id].credit -= 5
        await subtruck_genshins(telegram_id=message.from_user.id, credit=gdz_users[message.from_user.id].credit)
    await state.clear()

async def main() -> None:
    dp.include_router(main_router)
    await keyboards.create_keyboards()
    await get_data_for_users()
#    await message_to_all_users()
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())