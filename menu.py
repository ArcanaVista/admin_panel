from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .keyboards import admin_main_kb
from .goods.keyboards import admin_goods_kb
from .vpn.keyboards import admin_vpn_kb
from .bot.keyboards import admin_bot_kb
from .panel.keyboards import panel_main_kb
from .admin_functions.keyboards import admin_sections_kb

from app.utils import load_features, save_features, admin_only_callback

router = Router()


@router.callback_query(F.data == "admin_main")
@admin_only_callback
async def show_admin_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    admin_welcome_text = (
        "🛠 <b>Админ-панель</b>\n\n"
        "Выберите раздел для управления:"
    )
    try:
        await callback.message.edit_text(admin_welcome_text, reply_markup=admin_main_kb())
    except Exception:
        await callback.message.answer(admin_welcome_text, reply_markup=admin_main_kb())


@router.callback_query(F.data == "admin_vpn")
@admin_only_callback
async def show_admin_vpn(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    admin_vpn_text = (
        "🛡️ <b>VPN Outline</b>\n\n"
        "Выберите действие:"
    )
    try:
        await callback.message.edit_text(admin_vpn_text, reply_markup=admin_vpn_kb())
    except Exception:
        await callback.message.answer(admin_vpn_text, reply_markup=admin_vpn_kb())


@router.callback_query(F.data == "admin_bot")
@admin_only_callback
async def show_admin_bot(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    admin_bot_text = (
        "🤖 <b>Боты и скрипты</b>\n\n"
        "Выберите действие:"
    )
    try:
        await callback.message.edit_text(admin_bot_text, reply_markup=admin_bot_kb())
    except Exception:
        await callback.message.answer(admin_bot_text, reply_markup=admin_bot_kb())


@router.callback_query(F.data == "admin_goods")
@admin_only_callback
async def show_admin_goods(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    admin_goods_text = (
        "📦 <b>Цифровые товары</b>\n\n"
        "Выберите действие:"
    )
    try:
        await callback.message.edit_text(admin_goods_text, reply_markup=admin_goods_kb())
    except Exception:
        await callback.message.answer(admin_goods_text, reply_markup=admin_goods_kb())


@router.callback_query(F.data == "admin_services")
@admin_only_callback
async def panel_main_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📊 <b>Услуги под заказ</b>\n\n"
        "Выберите действие:",
        reply_markup=panel_main_kb()
    )


@router.callback_query(F.data == "admin_sections")
@admin_only_callback
async def show_admin_sections(callback: CallbackQuery):
    features = load_features()
    await callback.message.edit_text(
        "⚙️ <b>Разделы</b>\n\n"
        "Включить или отключить нужные разделы:",
        reply_markup=admin_sections_kb(features)
    )


@router.callback_query(F.data.startswith("toggle_"))
@admin_only_callback
async def toggle_section(callback: CallbackQuery):
    mapping = {
        "toggle_vpn": "vpn_outline",
        "toggle_bot": "bot",
        "toggle_goods": "goods",
        "toggle_services": "services",
    }
    features = load_features()
    key = mapping.get(callback.data)
    if key:
        features[key] = not features.get(key, True)
        save_features(features)
    await callback.message.edit_reply_markup(reply_markup=admin_sections_kb(features))


@router.callback_query(F.data == "admin_back")
@admin_only_callback
async def admin_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🔙 <b>Главное меню администратора</b>",
        reply_markup=admin_vpn_kb()
    )
