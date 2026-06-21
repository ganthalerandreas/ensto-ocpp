from fastapi import FastAPI, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

from app.ocpp_handler import ChargePointHandler

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ocpp/{cp_id}")
async def ocpp_endpoint(websocket: WebSocket, cp_id: str):

    await websocket.accept()

    cp = ChargePointHandler(cp_id, websocket)

    await cp.run()
