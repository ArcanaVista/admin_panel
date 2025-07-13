from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from sqlalchemy import select

from .keyboards import panel_main_kb, categories_kb, buttons_list_kb, action_type_kb
from .states import AddCatFSM, AddBtnFSM

from app.db import SessionLocal
from app.models import ButtonCategory, ActionButton
from app.utils import admin_only_message, admin_only_callback

router = Router()

def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="panel_main")
    builder.adjust(1)
    return builder.as_markup()

# --- Клавиатура категорий для списка кнопок ---
def button_categories_kb(categories) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat.name, callback_data=f"btn_cat_{cat.id}")
    builder.button(text="⬅️ Назад", callback_data="panel_main")
    builder.adjust(1)
    return builder.as_markup()

def buttons_list_kb(btns) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for b in btns:
        builder.button(text=f"{b.id} | {b.name}", callback_data=f"panel_btn_{b.id}")
    builder.button(text="⬅️ Назад", callback_data="panel_list_btns")  # назад к категориям
    builder.adjust(1)
    return builder.as_markup()

@router.callback_query(F.data == "panel_add_cat")
@admin_only_callback
async def add_cat_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCatFSM.name)
    await callback.message.edit_text("Введите название категории:", reply_markup=cancel_kb())

@router.message(AddCatFSM.name)
@admin_only_message
async def add_cat_done(message: Message, state: FSMContext):
    cat_name = message.text.strip()
    if not cat_name:
        await message.answer("Название не может быть пустым. Введите ещё раз:", reply_markup=cancel_kb())
        return
    async with SessionLocal() as session:
        # Найдём максимальный sort_order для категорий
        max_sort = (
            await session.execute(
                select(ButtonCategory.sort_order).order_by(ButtonCategory.sort_order.desc())
            )
        ).scalars().first() or 0
        cat = ButtonCategory(name=cat_name, sort_order=max_sort + 1)
        session.add(cat)
        await session.commit()
    await state.clear()
    await message.answer("✅ Категория добавлена", reply_markup=panel_main_kb())


@router.callback_query(F.data == "panel_add_btn")
@admin_only_callback
async def add_btn_start(callback: CallbackQuery, state: FSMContext):
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory))).scalars().all()
    if not cats:
        try:
            await callback.message.edit_text("Сначала создайте категорию", reply_markup=panel_main_kb())
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        return
    await state.set_state(AddBtnFSM.category)
    await callback.message.edit_text("Выберите категорию:", reply_markup=categories_kb(cats))

@router.callback_query(AddBtnFSM.category, F.data.startswith("panel_cat_"))
@admin_only_callback
async def add_btn_choose_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[-1])
    await state.update_data(category=cat_id)
    await state.set_state(AddBtnFSM.name)
    await callback.message.edit_text("Введите название кнопки:", reply_markup=cancel_kb())

@router.message(AddBtnFSM.name)
@admin_only_message
async def add_btn_name(message: Message, state: FSMContext):
    btn_name = message.text.strip()
    if not btn_name:
        await message.answer("Название не может быть пустым. Введите ещё раз:", reply_markup=cancel_kb())
        return
    await state.update_data(name=btn_name)
    await state.set_state(AddBtnFSM.description)
    await message.answer("Введите описание кнопки:", reply_markup=cancel_kb())

@router.message(AddBtnFSM.description)
@admin_only_message
async def add_btn_desc(message: Message, state: FSMContext):
    btn_desc = message.text.strip()
    if not btn_desc:
        await message.answer("Описание не может быть пустым. Введите ещё раз:", reply_markup=cancel_kb())
        return
    await state.update_data(description=btn_desc)
    await state.set_state(AddBtnFSM.type)
    await message.answer("Выберите тип действия:", reply_markup=action_type_kb())

@router.callback_query(AddBtnFSM.type, F.data.startswith("type_"))
@admin_only_callback
async def add_btn_type(callback: CallbackQuery, state: FSMContext):
    if callback.data == "type_back":
        await state.set_state(AddBtnFSM.name)
        await callback.message.edit_text("Введите название кнопки:", reply_markup=cancel_kb())
        return
    typ = callback.data.split("_")[-1]
    await state.update_data(type=typ)
    await state.set_state(AddBtnFSM.button_data)
    if typ == "request":
        prompt = "Введите вопрос для пользователя:"
    elif typ == "info":
        prompt = "Ссылка на мини‑приложение:"
    else:
        prompt = "Введите URL:"
    await callback.message.edit_text(prompt, reply_markup=cancel_kb())

@router.message(AddBtnFSM.button_data)
@admin_only_message
async def add_btn_data(message: Message, state: FSMContext, **_):
    text = message.text.strip()
    if not text:
        await message.answer("Поле не может быть пустым. Введите ещё раз:", reply_markup=cancel_kb())
        return
    # notify всегда True, approve всегда False (можешь поменять на True если надо!)
    await state.update_data(button_data=text, notify=True, approve=True)
    data = await state.get_data()
    # Получаем имя категории для подтверждения
    async with SessionLocal() as session:
        cat = await session.get(ButtonCategory, data['category'])
        cat_name = cat.name if cat else str(data['category'])
    text_confirm = (
        f"<b>Проверьте кнопку:</b>\n"
        f"Категория: {cat_name}\n"
        f"Название: {data['name']}\n"
        f"Описание: {data['description']}\n"
        f"Тип: {data['type']}\n"
        f"Данные: {data['button_data']}\n"
        f"Уведомлять: {'Да' if data['notify'] else 'Нет'}\n"
        f"Подтверждение: {'Да' if data['approve'] else 'Нет'}\n\n"
        "Добавить?"
    )
    await state.set_state(AddBtnFSM.confirm)
    builder = InlineKeyboardBuilder()
    builder.button(text="✅", callback_data="btn_confirm")
    builder.button(text="❌", callback_data="panel_main")
    builder.adjust(2)
    await message.answer(text_confirm, reply_markup=builder.as_markup())

@router.callback_query(AddBtnFSM.confirm, F.data == "btn_confirm")
@admin_only_callback
async def add_btn_save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with SessionLocal() as session:
        # Найдём максимальный sort_order для выбранной категории!
        max_sort = (
            await session.execute(
                select(ActionButton.sort_order)
                .where(ActionButton.category_id == data["category"])
                .order_by(ActionButton.sort_order.desc())
            )
        ).scalars().first() or 0

        btn = ActionButton(
            name=data["name"],
            description=data["description"],
            action_type=data["type"],
            data=data["button_data"],
            category_id=data["category"],
            admin_notify=data["notify"],
            requires_approval=data["approve"],
            sort_order=max_sort + 1,  # <-- вот тут сортировка!
        )
        session.add(btn)
        await session.commit()
    await state.clear()
    try:
        await callback.message.edit_text("✅ Кнопка добавлена", reply_markup=panel_main_kb())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


# # --- Новый способ: сначала категории, потом кнопки ---
# @router.callback_query(F.data == "panel_list_btns")
# @admin_only_callback
# async def list_buttons_categories(callback: CallbackQuery):
#     async with SessionLocal() as session:
#         cats = (await session.execute(select(ButtonCategory))).scalars().all()
#     if not cats:
#         await callback.message.edit_text("Нет категорий.", reply_markup=panel_main_kb())
#         return
#     await callback.message.edit_text(
#         "Выберите категорию:",
#         reply_markup=button_categories_kb(cats)
#     )

# @router.callback_query(F.data.startswith("btn_cat_"))
# @admin_only_callback
# async def list_buttons_in_category(callback: CallbackQuery):
#     cat_id = int(callback.data.split("_")[-1])
#     async with SessionLocal() as session:
#         btns = (await session.execute(
#             select(ActionButton).where(ActionButton.category_id == cat_id)
#         )).scalars().all()
#     if not btns:
#         await callback.message.edit_text("В этой категории нет кнопок.", reply_markup=panel_main_kb())
#         return
#     await callback.message.edit_text("Список кнопок:", reply_markup=buttons_list_kb(btns))

# @router.callback_query(F.data == "panel_main")
# @admin_only_callback
# async def cancel_fsm(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
#     try:
#         await callback.message.edit_text("Действие отменено.", reply_markup=panel_main_kb())
#     except TelegramBadRequest as e:
#         if "message is not modified" not in str(e):
#             raise
