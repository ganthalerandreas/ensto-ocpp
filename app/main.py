from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call_result
from ocpp.routing import on
import datetime

app = FastAPI()

current_status = "In attesa connessione"


class ChargePointHandler(CP):

    @on("BootNotification")
    async def on_boot(self, **kwargs):

        global current_status
        current_status = "Connessa"

        print("BootNotification ricevuto")

        return call_result.BootNotification(
            current_time=datetime.datetime.utcnow().isoformat(),
            interval=30,
            status="Accepted"
        )

    @on("StatusNotification")
    async def on_status(self, status, **kwargs):

        global current_status
        current_status = status

        print("STATUS:", status)

        return call_result.StatusNotification()


@app.get("/")
def home():

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    </head>
    <body>
    <h1>Wallbox Status</h1>
    <h2>{current_status}</h2>
    </body>
    </html>
    """)


@app.websocket("/ENSTO001")
async def websocket_endpoint(websocket: WebSocket):

    protocols = websocket.headers.get(
        "sec-websocket-protocol"
    )

    if protocols != "ocpp1.6":
        print("Subprotocol errato:", protocols)
        await websocket.close()
        return

    await websocket.accept(
        subprotocol="ocpp1.6"
    )

    print("Wallbox collegata")

    cp = ChargePointHandler(
        "ENSTO001",
        websocket
    )

    try:
        await cp.start()

    except WebSocketDisconnect:
        print("Wallbox disconnessa")
