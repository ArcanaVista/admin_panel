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