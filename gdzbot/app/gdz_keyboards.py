from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

class Keyboards:
    def __init__(self):
        self.main_buttons = {
                            "🖋 Сочинение/реферат и т.д.": 'free_writting',
                            "📷 Текст с фото": 'photo_analysis',
                            "👤 Мой профиль": 'user_profile',
                            "ℹ️ О боте": 'about_bot'
        }

        self.free_writting_buttons = {
                                    'Сочинение ✍️': 'сomposition',
                                    '📃Эссе': 'essay',
                                    'Сообщение 🖊': 'free_message',
                                    '📄 Реферат': 'abstract',
                                    '🖋️ Доклад': 'report',
                                    '📝 Изложение': 'exposition',
                                    'Другое 😇': 'other_writting',
                                    'Назад 🔙': 'back_to_main_menu'}


        self.back_to_main_menu_buttons = {
                                            'Назад 🔙': 'back_to_main_menu'}
        
        self.main_buttons_old = {
                            "🖋 Сочинение/реферат и т.д.": 'free_writting',
                            "📷 Текст с фото": 'photo_analysis',
                            "🧮 Математика": '3',
                            "🎨 Рисунок": '4',
                            "❓ Вопрос": '5',
                            "🇬🇧 Ин.яз.": '6',
                            "🎓 Тест": '7',
                            "😇 Другое": '8',
                            "👤 Мой профиль": 'user_profile',
                            "ℹ️ О боте": 'about_bot'
        }

    async def build_free_writing_keyboard(self) -> None:
        builder = InlineKeyboardBuilder()
        for index in range(len(self.free_writting_buttons)):
            builder.button(text=list(self.free_writting_buttons.keys())[index],
                           callback_data=list(self.free_writting_buttons.values())[index])
            builder.adjust(2,2,2,1,1)
        self.free_writting = builder.as_markup()

    async def build_main_keyboard(self) -> None:
        builder = InlineKeyboardBuilder()
        for index in range(len(self.main_buttons)):
            builder.button(text=list(self.main_buttons.keys())[index],
                           callback_data=list(self.main_buttons.values())[index])
            builder.adjust(2,3,3,2)
        self.main = builder.as_markup()

    async def build_back_to_main_menu_keyboard(self) -> None:
        builder = InlineKeyboardBuilder()
        for index in range(len(self.back_to_main_menu_buttons)):
            builder.button(text=list(self.back_to_main_menu_buttons.keys())[index],
                           callback_data=list(self.back_to_main_menu_buttons.values())[index])
        self.back_to_main_menu = builder.as_markup()


    async def create_keyboards(self):
        await self.build_main_keyboard()
        await self.build_free_writing_keyboard()
        await self.build_back_to_main_menu_keyboard()

    
