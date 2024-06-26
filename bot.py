import asyncio
import os
import tempfile

from aiogram import Bot, Dispatcher, types, F, filters
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from redis.asyncio import Redis

from config import settings
import gpt


class UserStates(StatesGroup):
    default = State()
    thread_id = State()


async def main():
    r = await Redis(host="redis", port=settings.port, decode_responses=True)

    dp = Dispatcher(storage=RedisStorage(redis=r))
    bot = Bot(token=settings.telegram_token)

    # Start command handler
    @dp.message(filters.CommandStart())
    async def start(message: types.Message, state: FSMContext):
        await state.set_state(UserStates.default)
        await message.reply("Привет, отправь мне голосовое сообщение!")

    # Voice message handler
    @dp.message(F.voice)
    async def handle_voice(message: types.Message, state: FSMContext):
        voice = await bot.get_file(message.voice.file_id)
        fd, voice_file_path = tempfile.mkstemp(suffix='.ogg')
        os.close(fd)
        await bot.download(voice, destination=voice_file_path)

        transcription_text = await gpt.speech_to_text(voice_file_path)

        if transcription_text.strip() == '':
            await message.reply("Извините, я не смог понять голосовое сообщение. Пожалуйста, попробуйте еще раз.")
        else:
            generated_text, thread_id = await gpt.text_generation(transcription_text)
            print(f"{transcription_text=}")
            print(f"{generated_text=}")
            speech_file_path = await gpt.text_to_speech(generated_text)
            await bot.send_voice(chat_id=message.chat.id, voice=FSInputFile(path=speech_file_path))
            os.remove(speech_file_path)

            # Save the thread_id in the state data
            await state.update_data(thread_id=thread_id)
            await state.set_state(UserStates.thread_id)

        os.remove(voice_file_path)

    # Handler to retrieve and display the thread_id
    @dp.message(UserStates.thread_id, F.text == "thread")
    async def prthread(message: types.Message, state: FSMContext):
        st = await state.get_data()
        dt = st.get("thread_id")
        await message.answer(dt)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
