from openai import AsyncOpenAI
import asyncio
import traceback

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
    def __init__(self,data =None,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs
        self.data = data

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

    async def easy_gpt(self,token,input, assistant_name,system_message):
            """ Передаем запрос к GPT, получаем ответ в виде листа: 
            [0] - ответ бота, [1] - общее количество токенов запроса, [2] - баланс API-ключа """
            try:
                client = AsyncOpenAI(api_key=token)
                assistant = await client.beta.assistants.create(
                            name=assistant_name,
                            instructions=system_message,
                            tools=[],
                            model="gpt-3.5-turbo")
                thread = await client.beta.threads.create()
                message = client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=input
                        )
                stream = await client.chat.completions.create(model='gpt-3.5-turbo', messages=[{"role": "user", "content": input}], stream=True)
                response = ""
                async for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        response += chunk.choices[0].delta.content
                return response
            except:
                print(traceback.format_exc())
                return [f'⚠️ Непредвиденная ошибка {traceback.format_exc()}',0,2]