from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .keyboards import (
    panel_main_kb,
    action_type_kb,
    edit_button_kb,
    button_categories_kb,
    categories_edit_kb,
    confirm_rename_kb,
    categories_delete_kb,
    confirm_delete_cat_kb,
    buttons_list_kb,
    categories_for_buttons_kb,
    buttons_delete_kb,
    confirm_delete_btn_kb,
    categories_sort_kb,
    buttons_sort_kb,
)
from .states import EditBtnFSM, EditCatFSM, DeleteCatFSM, DeleteBtnFSM, SortBtnFSM
from ..menu import panel_main_cb

from app.utils import admin_only_message, admin_only_callback
from app.models import ServiceRequest, ActionButton, ButtonCategory
from app.db import SessionLocal

router = Router()



CATS_PER_PAGE = 5
BTNS_PER_PAGE = 5

def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="panel_main")
    builder.adjust(1)
    return builder.as_markup()



@router.callback_query(F.data == "panel_list_btns")
@admin_only_callback
async def list_buttons_categories(callback: CallbackQuery):
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory))).scalars().all()
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=button_categories_kb(cats, page=0)
    )

@router.callback_query(F.data.regexp(r"^panel_list_btns_page_(\d+)$"))
@admin_only_callback
async def list_buttons_categories_page(callback: CallbackQuery):
    import re
    page = int(re.match(r"^panel_list_btns_page_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory))).scalars().all()
    total_pages = (len(cats) - 1) // CATS_PER_PAGE + 1
    await callback.message.edit_text(
        f"Выберите категорию (стр. {page+1}/{total_pages}):",
        reply_markup=button_categories_kb(cats, page=page)
    )

@router.callback_query(F.data.regexp(r"^btn_cat_(\d+)_page_(\d+)$"))
@admin_only_callback
async def list_buttons_in_category(callback: CallbackQuery, state: FSMContext):
    import re
    m = re.match(r"^btn_cat_(\d+)_page_(\d+)$", callback.data)
    cat_id = int(m.group(1))
    page = int(m.group(2))
    # Запоминаем текущую страницу категории
    await state.update_data(cat_id=cat_id, cat_page=page)
    async with SessionLocal() as session:
        btns = (await session.execute(
            select(ActionButton).where(ActionButton.category_id == cat_id)
        )).scalars().all()
    total_pages = (len(btns) - 1) // BTNS_PER_PAGE + 1
    await callback.message.edit_text(
        f"Список кнопок (стр. {page+1}/{total_pages}):",
        reply_markup=buttons_list_kb(btns, cat_id, page=page)
    )

@router.callback_query(F.data.regexp(r"^panel_btn_(\d+)_cat_(\d+)_page_(\d+)$"))
@admin_only_callback
async def edit_button_show(callback: CallbackQuery, state: FSMContext):
    import re
    m = re.match(r"^panel_btn_(\d+)_cat_(\d+)_page_(\d+)$", callback.data)
    btn_id = int(m.group(1))
    cat_id = int(m.group(2))
    page = int(m.group(3))
    # Сохраняем и cat_id, и page для возвратов
    await state.update_data(cat_id=cat_id, cat_page=page)
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        cat = await session.get(ButtonCategory, cat_id)
    if not btn:
        await callback.answer("Нет данных", show_alert=True)
        return
    text = (
        f"ID: {btn.id}\n"
        f"Категория: {cat.name if cat else f'ID {cat_id}'}\n"
        f"Название: {btn.name}\n"
        f"Описание: {btn.description}\n"
        f"Тип: {btn.action_type}\n"
        f"Данные: {btn.data}\n"
        f"Уведомлять: {'Да' if btn.admin_notify else 'Нет'}\n"
        f"Подтверждение: {'Да' if btn.requires_approval else 'Нет'}"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Название", callback_data=f"edit_name_panel_{btn_id}")
    builder.button(text="💬 Описание", callback_data=f"edit_desc_panel_{btn_id}")
    builder.button(text="⚡️ Тип", callback_data=f"edit_type_panel_{btn_id}")
    builder.button(text="📄 Данные", callback_data=f"edit_data_panel_{btn_id}")
    builder.button(text="🔔 Уведомлять", callback_data=f"toggle_notify_panel_{btn_id}")
    builder.button(text="✅ Требует выдачи", callback_data=f"toggle_approve_panel_{btn_id}")
    builder.button(text="🗑️ ❌ Удалить", callback_data=f"del_btn_panel_{btn_id}")
    builder.row(
        InlineKeyboardButton(text="⬅️ К кнопкам", callback_data=f"btn_cat_{cat_id}_page_{page}"),
        InlineKeyboardButton(text="⬅️ К категориям", callback_data="panel_list_btns"),
        InlineKeyboardButton(text="⬅️ В меню", callback_data="panel_main")
    )
    builder.adjust(2)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

# ===== Возврат к списку кнопок с учетом страницы =====
async def show_category_buttons(event, cat_id, is_message=False):
    # Получаем страницу из state, если она была сохранена, иначе 0
    page = 0
    if hasattr(event, 'from_user'):  # CallbackQuery
        state = FSMContext(event.bot, event.from_user.id, event.chat.id)
        data = await state.get_data()
        page = data.get('cat_page', 0)
    elif hasattr(event, 'from_id'):  # Message
        state = FSMContext(event.bot, event.from_id, event.chat.id)
        data = await state.get_data()
        page = data.get('cat_page', 0)
    async with SessionLocal() as session:
        btns = (await session.execute(
            select(ActionButton).where(ActionButton.category_id == cat_id)
        )).scalars().all()
    total_pages = (len(btns) - 1) // BTNS_PER_PAGE + 1 if btns else 1
    text = "Список кнопок:" if btns else "В этой категории нет кнопок."
    if is_message:
        await event.answer(
            text,
            reply_markup=buttons_list_kb(btns, cat_id, page=page)
        )
    else:
        await event.message.edit_text(
            f"{text} (стр. {page+1}/{total_pages}):",
            reply_markup=buttons_list_kb(btns, cat_id, page=page)
        )


@router.callback_query(F.data.startswith("edit_name_panel_"))
@admin_only_callback
async def edit_name_start(callback: CallbackQuery, state: FSMContext):
    btn_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    await state.update_data(btn_id=btn_id, field="name", cat_id=data.get("cat_id"))
    await state.set_state(EditBtnFSM.value)
    await callback.message.edit_text("Введите новое название:", reply_markup=cancel_kb())


@router.message(EditBtnFSM.value)
@admin_only_message
async def edit_value_save(message: Message, state: FSMContext):
    data = await state.get_data()
    btn_id = data.get("btn_id")
    field = data.get("field")
    cat_id = data.get("cat_id")
    text = message.text.strip()
    if not text:
        await message.answer("Значение не может быть пустым. Введите ещё раз:", reply_markup=cancel_kb())
        return
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        if btn and hasattr(btn, field):
            setattr(btn, field, text)
            await session.commit()
    await state.clear()
    # После сохранения можно вернуть пользователя к просмотру отредактированной кнопки:
    # await edit_button_show(callback, state) - если нужно показать кнопку
    await message.answer("Изменено.", reply_markup=panel_main_kb())


@router.callback_query(F.data.regexp(r"^edit_desc_panel_(\d+)$"))
@admin_only_callback
async def edit_desc_start(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^edit_desc_panel_(\d+)$", callback.data).group(1))
    data = await state.get_data()
    await state.update_data(btn_id=btn_id, field="description", cat_id=data.get("cat_id"))
    await state.set_state(EditBtnFSM.value)
    await callback.message.edit_text("Введите новое описание:", reply_markup=cancel_kb())

@router.callback_query(F.data.regexp(r"^edit_type_panel_(\d+)$"))
@admin_only_callback
async def edit_type_start(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^edit_type_panel_(\d+)$", callback.data).group(1))
    data = await state.get_data()
    await state.update_data(btn_id=btn_id, field="action_type", cat_id=data.get("cat_id"))
    await state.set_state(EditBtnFSM.field)
    await callback.message.edit_text("Выберите тип:", reply_markup=action_type_kb())

@router.callback_query(F.data.regexp(r"^edit_data_panel_(\d+)$"))
@admin_only_callback
async def edit_data_start(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^edit_data_panel_(\d+)$", callback.data).group(1))
    data = await state.get_data()
    await state.update_data(btn_id=btn_id, field="data", cat_id=data.get("cat_id"))
    await state.set_state(EditBtnFSM.value)
    await callback.message.edit_text("Введите новые данные:", reply_markup=cancel_kb())

@router.callback_query(F.data.regexp(r"^toggle_notify_panel_(\d+)$"))
@admin_only_callback
async def toggle_notify(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^toggle_notify_panel_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        if btn:
            btn.admin_notify = not btn.admin_notify
            await session.commit()
            await callback.answer("Готово", show_alert=True)
            # Получаем cat_id и cat_page из state
            data = await state.get_data()
            cat_id = data.get("cat_id")
            page = data.get("cat_page", 0)
            await edit_button_show(callback, state)
        else:
            await callback.answer("Нет данных", show_alert=True)
            await panel_main_cb(callback, state)

@router.callback_query(F.data.regexp(r"^toggle_approve_panel_(\d+)$"))
@admin_only_callback
async def toggle_approve(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^toggle_approve_panel_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        if btn:
            btn.requires_approval = not btn.requires_approval
            await session.commit()
            await callback.answer("Готово", show_alert=True)
            await edit_button_show(callback, state)
        else:
            await callback.answer("Нет данных", show_alert=True)
            await panel_main_cb(callback, state)

@router.callback_query(F.data.regexp(r"^del_btn_panel_(\d+)$"))
@admin_only_callback
async def delete_button(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^del_btn_panel_(\d+)$", callback.data).group(1))
    data = await state.get_data()
    cat_id = data.get("cat_id")
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        if btn:
            # Удаляем связанные заявки
            result = await session.execute(
                select(ServiceRequest).where(ServiceRequest.button_id == btn_id)
            )
            related_requests = result.scalars().all()
            for req in related_requests:
                await session.delete(req)
            await session.delete(btn)
            await session.commit()
            await callback.answer("Удалено", show_alert=True)
        else:
            await callback.answer("Кнопка не найдена", show_alert=True)
    await state.clear()
    # Возврат к списку кнопок этой категории!
    await show_category_buttons(callback, cat_id)






















































@router.callback_query(F.data == "edit_category")
@admin_only_callback
async def edit_category_start(callback: CallbackQuery, state: FSMContext):
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.id))).scalars().all()
    if not cats:
        await callback.message.edit_text("Категорий нет.", reply_markup=None)
        return
    total_pages = (len(cats) - 1) // CATS_PER_PAGE + 1
    await state.set_state(EditCatFSM.choose)
    await callback.message.edit_text(
        f"Выберите категорию для переименования (стр. 1/{total_pages}):",
        reply_markup=categories_edit_kb(cats, page=0, total_pages=total_pages)
    )

@router.callback_query(EditCatFSM.choose, F.data.regexp(r"^edit_category_page_(\d+)$"))
@admin_only_callback
async def edit_category_page(callback: CallbackQuery, state: FSMContext):
    import re
    page = int(re.match(r"^edit_category_page_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.id))).scalars().all()
    total_pages = (len(cats) - 1) // CATS_PER_PAGE + 1
    await callback.message.edit_text(
        f"Выберите категорию для переименования (стр. {page+1}/{total_pages}):",
        reply_markup=categories_edit_kb(cats, page=page, total_pages=total_pages)
    )

@router.callback_query(EditCatFSM.choose, F.data.regexp(r"^edit_cat_(\d+)_page_(\d+)$"))
@admin_only_callback
async def edit_category_choose(callback: CallbackQuery, state: FSMContext):
    import re
    m = re.match(r"^edit_cat_(\d+)_page_(\d+)$", callback.data)
    cat_id = int(m.group(1))
    page = int(m.group(2))
    await state.update_data(cat_id=cat_id, cat_page=page)
    await state.set_state(EditCatFSM.name)
    await callback.message.edit_text("Введите новое название категории:")

@router.message(EditCatFSM.name)
@admin_only_message
async def edit_category_name(message, state: FSMContext):
    data = await state.get_data()
    cat_id = data.get("cat_id")
    text = message.text.strip()
    if not text:
        await message.answer("Название не может быть пустым. Введите ещё раз:")
        return
    await state.update_data(new_name=text)
    await state.set_state(EditCatFSM.confirm)
    await message.answer(
        f"Вы действительно хотите переименовать категорию в:\n\n<b>{text}</b>?",
        reply_markup=confirm_rename_kb()
    )

@router.callback_query(EditCatFSM.confirm, F.data == "cat_rename_confirm")
@admin_only_callback
async def edit_category_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cat_id = data.get("cat_id")
    new_name = data.get("new_name")
    async with SessionLocal() as session:
        cat = await session.get(ButtonCategory, cat_id)
        if cat:
            cat.name = new_name
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                await callback.message.edit_text(
                    "❌ Категория с таким именем уже существует!\n"
                    "Введите другое название:",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main")]
                    ])
                )
                await state.set_state(EditCatFSM.name)
                return
            await state.clear()
            await callback.message.edit_text(
                "✅ Название категории изменено.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main")]
                ])
            )
        else:
            await callback.message.edit_text(
                "Категория не найдена.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="panel_main")]
                ])
            )
            await state.clear()
@router.callback_query(EditCatFSM.confirm, F.data == "cat_rename_cancel")
@admin_only_callback
async def edit_category_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Переименование отменено.")


@router.callback_query(F.data == "delete_category")
@admin_only_callback
async def delete_category_start(callback: CallbackQuery, state: FSMContext):
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.id))).scalars().all()
    if not cats:
        await callback.message.edit_text("Категорий нет.", reply_markup=panel_main_kb())
        return
    total_pages = (len(cats) - 1) // CATS_PER_PAGE + 1
    await state.set_state(DeleteCatFSM.choose)
    await callback.message.edit_text(
        f"Выберите категорию для удаления (стр. 1/{total_pages}):",
        reply_markup=categories_delete_kb(cats, page=0, total_pages=total_pages)
    )


@router.callback_query(DeleteCatFSM.choose, F.data.regexp(r"^del_category_page_(\d+)$"))
@admin_only_callback
async def delete_category_page(callback: CallbackQuery, state: FSMContext):
    import re
    page = int(re.match(r"^del_category_page_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.id))).scalars().all()
    total_pages = (len(cats) - 1) // CATS_PER_PAGE + 1
    await callback.message.edit_text(
        f"Выберите категорию для удаления (стр. {page+1}/{total_pages}):",
        reply_markup=categories_delete_kb(cats, page=page, total_pages=total_pages)
    )


@router.callback_query(DeleteCatFSM.choose, F.data.regexp(r"^del_cat_(\d+)_page_(\d+)$"))
@admin_only_callback
async def delete_category_confirm(callback: CallbackQuery, state: FSMContext):
    import re
    m = re.match(r"^del_cat_(\d+)_page_(\d+)$", callback.data)
    cat_id = int(m.group(1))
    page = int(m.group(2))
    await state.update_data(cat_id=cat_id, cat_page=page)
    await state.set_state(DeleteCatFSM.confirm)
    await callback.message.edit_text(
        "Удалить выбранную категорию и все связанные кнопки?",
        reply_markup=confirm_delete_cat_kb()
    )


@router.callback_query(DeleteCatFSM.confirm, F.data == "cat_delete_confirm")
@admin_only_callback
async def delete_category_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cat_id = data.get("cat_id")
    async with SessionLocal() as session:
        cat = await session.get(ButtonCategory, cat_id)
        if cat:
            btns = (await session.execute(select(ActionButton).where(ActionButton.category_id == cat_id))).scalars().all()
            for btn in btns:
                reqs = (await session.execute(select(ServiceRequest).where(ServiceRequest.button_id == btn.id))).scalars().all()
                for r in reqs:
                    await session.delete(r)
                await session.delete(btn)
            await session.delete(cat)
            await session.commit()
    await state.clear()
    await callback.message.edit_text("Категория удалена.", reply_markup=panel_main_kb())


@router.callback_query(DeleteCatFSM.confirm, F.data == "cat_delete_cancel")
@admin_only_callback
async def delete_category_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Удаление отменено.", reply_markup=panel_main_kb())


@router.callback_query(F.data == "delete_button")
@admin_only_callback
async def delete_button_start(callback: CallbackQuery, state: FSMContext):
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.sort_order))).scalars().all()
    if not cats:
        await callback.message.edit_text("Категорий нет.", reply_markup=panel_main_kb())
        return
    await state.set_state(DeleteBtnFSM.choose_cat)
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=categories_for_buttons_kb(cats, prefix="del_btn_cat"),
    )


@router.callback_query(DeleteBtnFSM.choose_cat, F.data.regexp(r"^del_btn_cat_(\d+)$"))
@admin_only_callback
async def delete_button_choose(callback: CallbackQuery, state: FSMContext):
    import re
    cat_id = int(re.match(r"^del_btn_cat_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        btns = (await session.execute(
            select(ActionButton).where(ActionButton.category_id == cat_id).order_by(ActionButton.sort_order)
        )).scalars().all()
    if not btns:
        await callback.message.edit_text("В этой категории нет кнопок.", reply_markup=panel_main_kb())
        await state.clear()
        return
    await state.update_data(cat_id=cat_id)
    await state.set_state(DeleteBtnFSM.choose_btn)
    await callback.message.edit_text(
        "Выберите кнопку для удаления:",
        reply_markup=buttons_delete_kb(btns, cat_id, page=0),
    )


@router.callback_query(DeleteBtnFSM.choose_btn, F.data.regexp(r"^del_btn_page_(\d+)_(\d+)$"))
@admin_only_callback
async def delete_button_page(callback: CallbackQuery, state: FSMContext):
    import re
    m = re.match(r"^del_btn_page_(\d+)_(\d+)$", callback.data)
    cat_id = int(m.group(1))
    page = int(m.group(2))
    async with SessionLocal() as session:
        btns = (await session.execute(
            select(ActionButton).where(ActionButton.category_id == cat_id).order_by(ActionButton.sort_order)
        )).scalars().all()
    await callback.message.edit_text(
        "Выберите кнопку для удаления:",
        reply_markup=buttons_delete_kb(btns, cat_id, page=page),
    )


@router.callback_query(DeleteBtnFSM.choose_btn, F.data.regexp(r"^del_btn_(\d+)_page_(\d+)$"))
@admin_only_callback
async def delete_button_confirm(callback: CallbackQuery, state: FSMContext):
    import re
    m = re.match(r"^del_btn_(\d+)_page_(\d+)$", callback.data)
    btn_id = int(m.group(1))
    page = int(m.group(2))
    await state.update_data(btn_id=btn_id, btn_page=page)
    await state.set_state(DeleteBtnFSM.confirm)
    await callback.message.edit_text(
        "Удалить выбранную кнопку?",
        reply_markup=confirm_delete_btn_kb(),
    )


@router.callback_query(DeleteBtnFSM.confirm, F.data == "btn_delete_confirm")
@admin_only_callback
async def delete_button_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    btn_id = data.get("btn_id")
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        if btn:
            reqs = (await session.execute(select(ServiceRequest).where(ServiceRequest.button_id == btn_id))).scalars().all()
            for r in reqs:
                await session.delete(r)
            await session.delete(btn)
            await session.commit()
    await state.clear()
    await callback.message.edit_text("Кнопка удалена.", reply_markup=panel_main_kb())


@router.callback_query(DeleteBtnFSM.confirm, F.data == "btn_delete_cancel")
@admin_only_callback
async def delete_button_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Удаление отменено.", reply_markup=panel_main_kb())


@router.callback_query(F.data == "sort_categories")
@admin_only_callback
async def sort_categories_start(callback: CallbackQuery):
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.sort_order))).scalars().all()
    if not cats:
        await callback.message.edit_text("Категорий нет.", reply_markup=panel_main_kb())
        return
    await callback.message.edit_text(
        "Сортировка категорий:",
        reply_markup=categories_sort_kb(cats),
    )


@router.callback_query(F.data.regexp(r"^cat_up_(\d+)$"))
@admin_only_callback
async def sort_category_up(callback: CallbackQuery):
    import re
    cat_id = int(re.match(r"^cat_up_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        cat = await session.get(ButtonCategory, cat_id)
        prev = (
            await session.execute(
                select(ButtonCategory)
                .where(ButtonCategory.sort_order < cat.sort_order)
                .order_by(ButtonCategory.sort_order.desc())
            )
        ).scalars().first()
        if prev:
            cat.sort_order, prev.sort_order = prev.sort_order, cat.sort_order
            await session.commit()
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.sort_order))).scalars().all()
    await callback.message.edit_reply_markup(reply_markup=categories_sort_kb(cats))


@router.callback_query(F.data.regexp(r"^cat_down_(\d+)$"))
@admin_only_callback
async def sort_category_down(callback: CallbackQuery):
    import re
    cat_id = int(re.match(r"^cat_down_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        cat = await session.get(ButtonCategory, cat_id)
        nxt = (
            await session.execute(
                select(ButtonCategory)
                .where(ButtonCategory.sort_order > cat.sort_order)
                .order_by(ButtonCategory.sort_order)
            )
        ).scalars().first()
        if nxt:
            cat.sort_order, nxt.sort_order = nxt.sort_order, cat.sort_order
            await session.commit()
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.sort_order))).scalars().all()
    await callback.message.edit_reply_markup(reply_markup=categories_sort_kb(cats))


@router.callback_query(F.data == "sort_buttons")
@admin_only_callback
async def sort_buttons_choose_cat(callback: CallbackQuery, state: FSMContext):
    async with SessionLocal() as session:
        cats = (await session.execute(select(ButtonCategory).order_by(ButtonCategory.sort_order))).scalars().all()
    if not cats:
        await callback.message.edit_text("Категорий нет.", reply_markup=panel_main_kb())
        return
    await state.set_state(SortBtnFSM.choose_cat)
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=categories_for_buttons_kb(cats, prefix="sort_btn_cat"),
    )


@router.callback_query(SortBtnFSM.choose_cat, F.data.regexp(r"^sort_btn_cat_(\d+)$"))
@admin_only_callback
async def sort_buttons_start(callback: CallbackQuery, state: FSMContext):
    import re
    cat_id = int(re.match(r"^sort_btn_cat_(\d+)$", callback.data).group(1))
    async with SessionLocal() as session:
        btns = (
            await session.execute(
                select(ActionButton).where(ActionButton.category_id == cat_id).order_by(ActionButton.sort_order)
            )
        ).scalars().all()
    if not btns:
        await callback.message.edit_text("В этой категории нет кнопок.", reply_markup=panel_main_kb())
        await state.clear()
        return
    await state.update_data(cat_id=cat_id)
    await state.set_state(SortBtnFSM.sort)
    await callback.message.edit_text(
        "Сортировка кнопок:",
        reply_markup=buttons_sort_kb(btns, cat_id),
    )


@router.callback_query(SortBtnFSM.sort, F.data.regexp(r"^btn_up_(\d+)$"))
@admin_only_callback
async def sort_button_up(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^btn_up_(\d+)$", callback.data).group(1))
    data = await state.get_data()
    cat_id = data.get("cat_id")
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        prev = (
            await session.execute(
                select(ActionButton)
                .where(ActionButton.category_id == cat_id, ActionButton.sort_order < btn.sort_order)
                .order_by(ActionButton.sort_order.desc())
            )
        ).scalars().first()
        if prev:
            btn.sort_order, prev.sort_order = prev.sort_order, btn.sort_order
            await session.commit()
        btns = (
            await session.execute(
                select(ActionButton).where(ActionButton.category_id == cat_id).order_by(ActionButton.sort_order)
            )
        ).scalars().all()
    await callback.message.edit_reply_markup(reply_markup=buttons_sort_kb(btns, cat_id))


@router.callback_query(SortBtnFSM.sort, F.data.regexp(r"^btn_down_(\d+)$"))
@admin_only_callback
async def sort_button_down(callback: CallbackQuery, state: FSMContext):
    import re
    btn_id = int(re.match(r"^btn_down_(\d+)$", callback.data).group(1))
    data = await state.get_data()
    cat_id = data.get("cat_id")
    async with SessionLocal() as session:
        btn = await session.get(ActionButton, btn_id)
        nxt = (
            await session.execute(
                select(ActionButton)
                .where(ActionButton.category_id == cat_id, ActionButton.sort_order > btn.sort_order)
                .order_by(ActionButton.sort_order)
            )
        ).scalars().first()
        if nxt:
            btn.sort_order, nxt.sort_order = nxt.sort_order, btn.sort_order
            await session.commit()
        btns = (
            await session.execute(
                select(ActionButton).where(ActionButton.category_id == cat_id).order_by(ActionButton.sort_order)
            )
        ).scalars().all()
    await callback.message.edit_reply_markup(reply_markup=buttons_sort_kb(btns, cat_id))
