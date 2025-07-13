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

def categories_sort_kb(cats) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in cats:
        builder.row(
            InlineKeyboardButton(text=f"⬆️ {cat.name}", callback_data=f"cat_up_{cat.id}"),
            InlineKeyboardButton(text="⬇️", callback_data=f"cat_down_{cat.id}"),
        )
    builder.row(InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main"))
    return builder.as_markup()

# --- Selecting category for button actions ---

def categories_for_buttons_kb(cats, prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in cats:
        builder.button(text=cat.name, callback_data=f"{prefix}_{cat.id}")
    builder.button(text="⬅️ В админ-панель", callback_data="panel_main")
    builder.adjust(1)
    return builder.as_markup()
