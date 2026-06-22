from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.ocpp_server import start_ocpp_server

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "../templates")), name="static")


@app.on_event("startup")
async def startup():
    import asyncio
    asyncio.create_task(start_ocpp_server())


@app.get("/")
def home():
    html = open(os.path.join(BASE_DIR, "../templates/index.html")).read()
    return HTMLResponse(html)
