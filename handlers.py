from aiogram import Router

from .vpn import router as vpn_router
from .goods import router as goods_router
from .bot import router as admin_bot_router
from .panel import router as panel_router
from .admin_functions import router as admin_functions_router

from . import menu

router = Router()

router.include_router(admin_bot_router)
router.include_router(goods_router)
router.include_router(vpn_router)
router.include_router(panel_router)
router.include_router(admin_functions_router)
router.include_router(menu.router)

__all__ = ["router"]