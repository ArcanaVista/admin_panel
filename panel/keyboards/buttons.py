from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BTNS_PER_PAGE = 5


def buttons_list_kb(btns, cat_id, page=0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * BTNS_PER_PAGE
    end = start + BTNS_PER_PAGE
    btns_on_page = btns[start:end]
    for b in btns_on_page:
        builder.button(text=b.name, callback_data=f"panel_btn_{b.id}_cat_{cat_id}_page_{page}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"btn_cat_{cat_id}_page_{page-1}"))
    if end < len(btns):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"btn_cat_{cat_id}_page_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ К категориям", callback_data="panel_list_btns"))
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()


def edit_button_kb(btn_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Название", callback_data=f"edit_name_panel_{btn_id}")
    builder.button(text="💬 Описание", callback_data=f"edit_desc_panel_{btn_id}")
    builder.button(text="⚡️ Тип", callback_data=f"edit_type_panel_{btn_id}")
    builder.button(text="📄 Данные", callback_data=f"edit_data_panel_{btn_id}")
    builder.button(text="🔔 Уведомлять", callback_data=f"toggle_notify_panel_{btn_id}")
    builder.button(text="✅ Требует выдачи", callback_data=f"toggle_approve_panel_{btn_id}")
    builder.button(text="🗑️ ❌ Удалить", callback_data=f"del_btn_panel_{btn_id}")
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


# --- Delete buttons ---

def buttons_delete_kb(btns, cat_id, page=0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * BTNS_PER_PAGE
    end = start + BTNS_PER_PAGE
    btns_on_page = btns[start:end]
    for b in btns_on_page:
        builder.button(text=b.name, callback_data=f"del_btn_{b.id}_page_{page}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"del_btn_page_{cat_id}_{page-1}"))
    if end < len(btns):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"del_btn_page_{cat_id}_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ К категориям", callback_data="delete_button"))
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()


def confirm_delete_btn_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="btn_delete_confirm")
    builder.button(text="❌ Нет", callback_data="btn_delete_cancel")
    builder.adjust(2)
    return builder.as_markup()

# --- Sorting buttons ---

def buttons_sort_list_kb(btns, cat_id, page=0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * BTNS_PER_PAGE
    end = start + BTNS_PER_PAGE
    btns_on_page = btns[start:end]
    for b in btns_on_page:
        builder.button(text=f"{b.sort_order}. {b.name}", callback_data=f"reorder_btn_{b.id}_{page}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"sort_btn_cat_{cat_id}_page_{page-1}"))
    if end < len(btns):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"sort_btn_cat_{cat_id}_page_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ Категории", callback_data="sort_buttons"))
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()


def button_sort_actions_kb(btn_id: int, cat_id: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬆️ Вверх", callback_data=f"reorder_up_btn_{btn_id}_{cat_id}_{page}")
    builder.button(text="⬇️ Вниз", callback_data=f"reorder_down_btn_{btn_id}_{cat_id}_{page}")
    builder.button(text="⬅️ Назад", callback_data=f"sort_btn_cat_{cat_id}_page_{page}")
    builder.adjust(1)
    return builder.as_markup()
