from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

class Keyboards:
    def __init__(self):
        self.main_buttons = {
                            "🖋 Сочинение/реферат и т.д.": 'free_writting',
                            "📷 Текст с фото": '2',
                            "🧮 Математика": '3',
                            "🎨 Рисунок": '4',
                            "❓ Вопрос": '5',
                            "🇬🇧 Ин.яз.": '6',
                            "🎓 Тест": '7',
                            "😇 Другое": '8',
                            "👤 Мой профиль": '9',
                            "ℹ️ О боте": '10'
        }

        self.free_writting_buttons = {
                                    'Сочинение ✍️': 'сomposition',
                                    'Эссе ✍️': 'essay',
                                    'Сообщение ✍️': 'free_message',
                                    '📄 Реферат': 'abstract',
                                    '🖋️ Доклад': 'report',
                                    '📝 Изложение': 'exposition',
                                    'Другое': '😇',
                                    'Назад 🔙': 'back_to_menu'}


    async def build_free_writing_keyboard(self) -> None:
        builder = InlineKeyboardBuilder()
        for index in range(len(self.free_writting_buttons)-1):
            builder.button(text=list(self.free_writting_buttons.keys())[index],
                           callback_data=list(self.free_writting_buttons.values())[index])
            builder.adjust(2,2,2,1,1)
        self.free_writting = builder.as_markup()

    async def build_main_keyboard(self) -> None:
        builder = InlineKeyboardBuilder()
        for index in range(len(self.main_buttons)-1):
            builder.button(text=list(self.main_buttons.keys())[index],
                           callback_data=list(self.main_buttons.values())[index])
            builder.adjust(2,3,3,2)
        self.main = builder.as_markup()

    async def create_keyboards(self):
        await self.build_main_keyboard()
        await self.build_free_writing_keyboard()
