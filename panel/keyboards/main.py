from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def panel_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить категорию", callback_data="panel_add_cat")
    builder.button(text="➕ Добавить кнопку", callback_data="panel_add_btn")
    builder.button(text="✏️ Редактировать категорию", callback_data="edit_category")
    builder.button(text="✏️ Редактировать кнопку", callback_data="panel_list_btns")
    builder.button(text="❌ Удалить категорию", callback_data="delete_category")
    builder.button(text="❌ Удалить кнопку", callback_data="delete_button")
    builder.button(text="↕️ Сортировать категории", callback_data="sort_categories")
    builder.button(text="↕️ Сортировать кнопки", callback_data="sort_buttons")
    builder.button(text="⬅️ Назад", callback_data="admin_main")
    builder.adjust(2, 1, 1, 2, 1)
    return builder.as_markup()
