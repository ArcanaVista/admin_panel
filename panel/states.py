from aiogram.fsm.state import StatesGroup, State

class AddCatFSM(StatesGroup):
    name = State()

class AddBtnFSM(StatesGroup):
    category = State()
    name = State()
    description = State()
    type = State()
    button_data = State()   # <-- вот так!
    notify = State()
    approve = State()
    confirm = State()
    
class EditBtnFSM(StatesGroup):
    field = State()
    value = State()


class EditCatFSM(StatesGroup):
    choose = State()
    name = State()
    confirm = State()


class DeleteCatFSM(StatesGroup):
    choose = State()
    confirm = State()


class DeleteBtnFSM(StatesGroup):
    choose_cat = State()
    choose_btn = State()
    confirm = State()


class SortCatFSM(StatesGroup):
    choose = State()
    action = State()


class SortBtnFSM(StatesGroup):
    choose_cat = State()
    choose_btn = State()
    action = State()
