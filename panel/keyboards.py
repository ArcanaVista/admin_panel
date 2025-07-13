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


def categories_kb(cats) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for c in cats:
        builder.button(text=c.name, callback_data=f"panel_cat_{c.id}")
    builder.button(text="⬅️ Отмена", callback_data="admin_services")
    builder.adjust(1)
    return builder.as_markup()


def buttons_list_kb(btns) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for b in btns:
        builder.button(text=f"{b.id} | {b.name}", callback_data=f"panel_btn_{b.id}")
    builder.button(text="⬅️ Назад", callback_data="panel_main")
    builder.adjust(1)
    return builder.as_markup()


def edit_button_kb(btn_id: int) -> InlineKeyboardMarkup:


    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Название", callback_data=f"edit_name_{btn_id}")
    builder.button(text="💬 Описание", callback_data=f"edit_desc_{btn_id}")
    builder.button(text="⚡️ Тип", callback_data=f"edit_type_{btn_id}")
    builder.button(text="📄 Данные", callback_data=f"edit_data_{btn_id}")
    builder.button(text="🔔 Уведомлять", callback_data=f"toggle_notify_{btn_id}")
    builder.button(text="✅ Требует выдачи", callback_data=f"toggle_approve_{btn_id}")
    builder.button(text="🗑️ ❌ Удалить", callback_data=f"del_btn_{btn_id}")
    builder.adjust(2)
    return builder.as_markup()


def action_type_kb() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    builder.button(text="request", callback_data="type_request")
    builder.button(text="info", callback_data="type_info")
    builder.button(text="link", callback_data="type_link")
    builder.button(text="⬅️ Назад", callback_data="type_back")
    builder.adjust(1)
    return builder.as_markup()