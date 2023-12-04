import asyncio, openai
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, callback_query, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp, WebAppInfo, ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import os
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment



openai.api_key = "sk-or-vv-3677b56a5e03615c1b664481c9c37b42d8c101df676d6d11a509620d15fa1e7f" 
openai.base_url = "https://api.vsegpt.ru:6070/v1/"
model_ai = "openai/gpt-3.5-turbo"
ADMIN = '821785013'

class TutorUtl:
    url1 = 'https://skillbox.ru/media/growth/financial-literacy/'
    url2 = 'https://www.tinkoff.ru/finance/blog/money-management/'
    url3 = 'https://invlab.ru/financy/chto-takoe-finansovaya-gramotnost/'
    game = 'https://fin-quest.vercel.app/'


bot = Bot(token='6819023389:AAEnad3O25CpcS7v2N4ePuYgmaTtyvAbhS8')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
router = Router()

class UserState(StatesGroup):
    form = State()
    ask = State()

async def main():
    folder_path = 'audio'
    files = os.listdir(folder_path)
    for file in files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)
    print('start')
    await dp.start_polling(bot)

@dp.message(Command('start'))
async def start(message: Message):
    with open('id.txt', 'r+') as a:
        new = True
        for i in a:
            if str(message.chat.id) == i.strip():
                new = False
        if new == True:
            print(message.chat.id, file=a)

    markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пройти обучение🧑‍🏫", callback_data='instruction')
            ]
        ]
    )
    await message.answer(text=f'''Приветствую вас, {message.chat.first_name}! ✨🤖
Я - ФинМаестро💵, ваш надежный помощник в финансовых вопросах. Моя основная цель - защитить вас от финансовых мошенников и предоставить надежные сведения о ваших контактирующих лицах.
Давайте сначала пройдём обучение👨‍🏫
''', reply_markup=markup)



@dp.callback_query()
async def callbacks(callback: callback_query, state: FSMContext):
    if callback.data == 'instruction':
        print(await state.get_state())
        await callback.answer()
        markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Skillbox", web_app=WebAppInfo(url=TutorUtl.url1))
                ],
                [
                    InlineKeyboardButton(text="Tinkoff", web_app=WebAppInfo(url=TutorUtl.url2))
                ],
                [
                    InlineKeyboardButton(text="Invlab", web_app=WebAppInfo(url=TutorUtl.url3))
                ],
                [
                    InlineKeyboardButton(text="Дальше➡️", callback_data='main')
                ]
            ]
        )
        await callback.message.answer('''💳Мы предлагаем вам изучить несколько статей от популярных агрегаторов о финансовой грамоте''', reply_markup=markup)

    elif callback.data == 'main':
        await callback.answer()
        markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Спросить бота❓", callback_data='ask')
                ],
                [
                    InlineKeyboardButton(text="Анкетирование📋", callback_data='form')
                ],
                [
                    InlineKeyboardButton(text="Игра🎮", web_app=WebAppInfo(url=TutorUtl.game))
                ]
            ]
        )
        await callback.message.answer('''Меню🏠
❓Здесь вы можете спросить у бота различные вопросы по финансовой грамотности или мошенниках, поддержка голосовых сообщений включена

📋Еще вы можете пройти анкетирование о мошенническом случае, произошедшем с вами

🎮Также мы предусмотрели игру по финансовой грамотности''', reply_markup=markup)

    elif callback.data == 'form':
        await callback.answer()
        await callback.message.answer('''Напишите подробности мошеннического случая, произошедшего с вами''')
        await state.set_state(UserState.form)
    elif callback.data == 'ask':
        await callback.answer()
        await callback.message.answer('''Напишите ваш вопрос о финансовой грамотности''')
        await state.set_state(UserState.ask)

@dp.message(UserState.form)
async def form(message: Message, state: FSMContext) -> None:
    await state.clear()
    markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Меню🏠", callback_data='main')
            ]
        ]
    )
    await message.answer('Мы учли ваше обращение, мы свяжемся с вами в ближайшее время', reply_markup=markup)
    await bot.send_message(ADMIN, f'{message.chat.id}id\nname: {message.chat.first_name}\n@{message.chat.username}\n\ntext: {message.text}')


@dp.message(UserState.ask)
async def ask(message: Message, state: FSMContext) -> None:
    await state.clear()
    markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Меню🏠", callback_data='main')
            ]
        ]
    )
    if message.content_type == ContentType.TEXT:
        try:
            response = openai.chat.completions.create(
                model=model_ai,
                messages=[{"role": "user", "content": message.text}],
            )
            a = response.choices[0].message.content
        except Exception:
            a = 'Произошла ошибка при получении ответа от нейронной сети'
        await message.answer(a, reply_markup=markup)

    elif message.content_type == ContentType.VOICE:
        try:
            file_id = message.voice.file_id
            file_path = await bot.get_file(file_id)
            file = await bot.download_file(file_path.file_path)
            audio_file = f'audio/{file_id}.ogg'
            audio_wav = f'audio/{file_id}.wav'
            with open(audio_file, 'wb') as f:
                f.write(file.read())

            sound = AudioSegment.from_ogg(audio_file)
            sound.export(audio_wav, format='wav')

            r = sr.Recognizer()
            with sr.AudioFile(audio_wav) as source:
                audio = r.record(source)

            a = 'Распознано: '
            text = r.recognize_google(audio, language='ru-RU')
            a += text
        except sr.UnknownValueError:
            a = 'Произошла ошибка при распознавании аудио'
        except sr.RequestError as e:
            a = 'Произошла ошибка при распознавании аудио'
        except Exception as e:
            a = 'Произошла ошибка при распознавании аудио'
        await message.answer(a)

        try:
            response = openai.chat.completions.create(
                model=model_ai,
                messages=[{"role": "user", "content": text}],
            )
            a = response.choices[0].message.content
        except Exception:
            a = 'Произошла ошибка при получении ответа от нейронной сети'
        await message.answer(a, reply_markup=markup)


@dp.message()
async def ques(message: Message) -> None:
    if str(message.chat.id) == ADMIN:
        if message.reply_to_message:
            text = message.reply_to_message.text
            id = text.split('id')[0]
            await bot.send_message(id, message.text)
        elif not message.reply_to_message:
            with open('id.txt', 'r') as a:
                for id in a:
                    if message.text:
                        await bot.send_message(chat_id=id, text=message.text)




if __name__ == '__main__':
    while True:
        try:
            print(f'{datetime.now()}')
            asyncio.run(main())
        except Exception as e:
            with open('errors.txt', 'a+') as errors:
                print(f'{datetime.now()}    {e}', file=errors)
            print(e)
            continue
    