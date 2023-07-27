from fastapi import APIRouter

from my_api import api

routes = APIRouter()

routes.include_router(api.router)
