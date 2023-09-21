import asyncio
import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot, scheduler
from .inline import InlineKeyboard
from tgbot.misc.states import AdminFSM
from tgbot.models.redis_connector import TickersRedis
from ...misc.scheduler import SchedulerAPI
from ...services.excel import ExcelFile

router = Router()
# router.message.filter(AdminFilter())
# router.callback_query.filter(AdminFilter())

inline = InlineKeyboard()
excel = ExcelFile()


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    text = "Главное меню"
    kb = inline.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = "Главное меню"
    kb = inline.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "tickers")
async def main_block(callback: CallbackQuery, state: FSMContext):
    file_name = excel.tickers_path
    tickers = TickersRedis.get_all()
    excel.create_tickers_file(tickers=tickers)
    file = FSInputFile(path=file_name, filename=file_name)
    text = "Заполните файл с тикерами в колонку. После загрузки файла текущий ци"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.tickers)
    await callback.message.answer_document(document=file, caption=text, reply_markup=kb)
    os.remove(path=file_name)
    await bot.answer_callback_query(callback.id)


@router.message(F.document, AdminFSM.tickers)
async def main_block(message: Message, state: FSMContext):
    file_name = excel.tickers_path
    await bot.download(file=message.document, destination=file_name)
    file_data = excel.read_tickers_file()
    text = "Некорректные данные"
    if file_data:
        TickersRedis.create(tickers=file_data)
        text = f"В список перезаписано {len(file_data)} тикеров"
        await state.set_state(AdminFSM.home)
        scheduler.remove_all_jobs()
        await asyncio.sleep(5)
        await SchedulerAPI.main_dispatcher()
    os.remove(path=file_name)
    kb = inline.home_kb()
    await message.answer(text, reply_markup=kb)
