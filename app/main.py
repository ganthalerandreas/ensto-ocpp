import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.ocpp_handler import ChargePointHandler

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "../templates")
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "../static")),
    name="static"
)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
