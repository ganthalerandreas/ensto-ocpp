from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.ocpp_handler import ChargePointHandler
from app.init_db import init_db

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ocpp/{cp_id}")
async def ocpp(ws: WebSocket, cp_id: str):
    await ws.accept()

    cp = ChargePointHandler(cp_id, ws)
    await cp.run()
