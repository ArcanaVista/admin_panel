from aiogram import Router

router = Router()

from . import main, edit

router.include_router(main.router)
router.include_router(edit.router)

__all__ = ["router"]
