from openai import AsyncOpenAI
import asyncio
import traceback
import requests
import time

class Helper:
    """ Класс помощник для бота """
    def __init__(self,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs

    async def ellipsis(self,bot,message,message_id):
        while True:
            for dot in range(1,4):
                await bot.edit_message_text('.'*dot, message.chat.id, message_id)
                await asyncio.sleep(0.2)


class DotDict(dict):
    """Возврат информации через точку"""
    def __getattr__(self, attr):
        return self.get(attr)


class GptAdaper:
    """ Класс помощник для бота """
    def __init__(self,token=None,data =None,*args,**kwargs):
        self.__token = token
        self.args = args
        self.kwargs = kwargs
        self.data = data
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.__token}',
                        'OpenAI-Beta': 'assistants=v1'}

    def __getattr__(self, attr):
        return self.data.get(attr)
    
    def updata_data(self,new_data):
        """ Добавляем словарь """
        self.data = new_data


    def get_user_data(self, telegram_id):
        """ Находим юзера по telegram_id """
        user_data = self.data.get(telegram_id) if self.data else None
        return DotDict(user_data) if user_data else None
    def all_data(self):
        """ Все пользователи """
        return self.data

    async def easy_gpt(self,token,input):
            """ Передаем запрос к GPT, получаем ответ в виде листа: 
            [0] - ответ бота, [1] - общее количество токенов запроса, [2] - баланс API-ключа """
            try:
                client = AsyncOpenAI(api_key=token)
                thread = await client.beta.threads.create()
                await client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=input
                        )
                run = await client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id='asst_gu0muWvx44tALnw0aBzvjzNW'
                    )
                attempts = 0
                while run.status != 'completed' and attempts < 10:
                    run = await client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    print(run.status)
                    time.sleep(6)
                    attempts += 1

                messages = await client.beta.threads.messages.list(thread_id=thread.id)
                response = messages.data[0].content[0].text.value
                a = 1
                b = 2
                return response
            except:
                print(traceback.format_exc())
                return [f'⚠️ Непредвиденная ошибка {traceback.format_exc()}',0,2]