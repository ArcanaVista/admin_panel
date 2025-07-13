from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def admin_main_kb() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Реквизиты", callback_data="card_add")
    builder.button(text="💰 Начислить баланс", callback_data="admin_add_balance")
    builder.button(text="⚙️ Разделы", callback_data="admin_sections")
    builder.button(text="🔧 VPN Outline", callback_data="admin_vpn")
    builder.button(text="🤖 Боты & Скрипты", callback_data="admin_bot")
    builder.button(text="📦 Цифровые товары", callback_data="admin_goods")
    builder.button(text="📊 Услуги под заказ", callback_data="admin_services")
    builder.button(text="⬅️ В главное меню", callback_data="main_menu")

    builder.adjust(2, 1, 2)
    return builder.as_markup()

