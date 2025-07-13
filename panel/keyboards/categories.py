from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CATS_PER_PAGE = 5


def button_categories_kb(cats, page=0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * CATS_PER_PAGE
    end = start + CATS_PER_PAGE
    cats_on_page = cats[start:end]
    for cat in cats_on_page:
        builder.button(text=cat.name, callback_data=f"btn_cat_{cat.id}_page_{page}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"panel_list_btns_page_{page-1}"))
    if end < len(cats):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"panel_list_btns_page_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="panel_main"))
    return builder.as_markup()


def categories_kb(cats) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for c in cats:
        builder.button(text=c.name, callback_data=f"panel_cat_{c.id}")
    builder.button(text="⬅️ Отмена", callback_data="admin_services")
    builder.adjust(1)
    return builder.as_markup()


# --- Editing categories ---

def categories_edit_kb(cats, page=0, total_pages=1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * CATS_PER_PAGE
    end = start + CATS_PER_PAGE
    cats_on_page = cats[start:end]
    for cat in cats_on_page:
        builder.button(text=f"{cat.name} ({cat.id})", callback_data=f"edit_cat_{cat.id}_page_{page}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"edit_category_page_{page-1}"))
    if end < len(cats):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"edit_category_page_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()


def confirm_rename_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="cat_rename_confirm")
    builder.button(text="❌ Нет", callback_data="cat_rename_cancel")
    builder.adjust(2)
    return builder.as_markup()

# --- Deleting categories ---

def categories_delete_kb(cats, page=0, total_pages=1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * CATS_PER_PAGE
    end = start + CATS_PER_PAGE
    cats_on_page = cats[start:end]
    for cat in cats_on_page:
        builder.button(text=f"{cat.name} ({cat.id})", callback_data=f"del_cat_{cat.id}_page_{page}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"del_category_page_{page-1}"))
    if end < len(cats):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"del_category_page_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()


def confirm_delete_cat_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="cat_delete_confirm")
    builder.button(text="❌ Нет", callback_data="cat_delete_cancel")
    builder.adjust(2)
    return builder.as_markup()

# --- Sorting categories ---

def categories_sort_list_kb(cats, page=0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * CATS_PER_PAGE
    end = start + CATS_PER_PAGE
    cats_on_page = cats[start:end]
    for c in cats_on_page:
        builder.button(text=f"{c.sort_order}. {c.name}", callback_data=f"reorder_cat_{c.id}_{page}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"sort_categories_page_{page-1}"))
    if end < len(cats):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"sort_categories_page_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()


def category_sort_actions_kb(cat_id: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬆️ Вверх", callback_data=f"reorder_up_cat_{cat_id}_{page}")
    builder.button(text="⬇️ Вниз", callback_data=f"reorder_down_cat_{cat_id}_{page}")
    builder.button(text="⬅️ Назад", callback_data=f"sort_categories_page_{page}")
    builder.adjust(1)
    return builder.as_markup()

# --- Selecting category for button actions ---

def categories_for_buttons_kb(cats, prefix: str, page=0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * CATS_PER_PAGE
    end = start + CATS_PER_PAGE
    cats_on_page = cats[start:end]
    for cat in cats_on_page:
        builder.button(text=cat.name, callback_data=f"{prefix}_{cat.id}_page_0")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"sort_buttons_page_{page-1}"))
    if end < len(cats):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"sort_buttons_page_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()
