from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from ocpp.v16 import ChargePoint
from ocpp.v16 import call_result
from ocpp.v16.call_result import BootNotification
from ocpp.routing import on
import datetime

app = FastAPI()

current_status = "In attesa connessione..."


# Adattatore: trasforma WebSocket FastAPI
# nel formato richiesto dalla libreria OCPP
class WebSocketAdapter:

    def __init__(self, websocket):
        self.websocket = websocket

    async def recv(self):
        return await self.websocket.receive_text()

    async def send(self, message):
        await self.websocket.send_text(message)


class CP(ChargePoint):

    @on("BootNotification")
    async def on_boot(self, **kwargs):

        global current_status

        current_status = "Connessa"

        print("BootNotification ricevuto")

        return BootNotification(
            current_time=datetime.datetime.utcnow().isoformat(),
            interval=30,
            status="Accepted"
        )

    @on("StatusNotification")
    async def on_status(self, status, **kwargs):

        global current_status

        current_status = status

        print("STATUS:", status)


@app.get("/")
def home():

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <body>

    <h1>Wallbox Status</h1>

    <h2>{current_status}</h2>

    </body>
    </html>
    """)


@app.websocket("/ENSTO001")
async def websocket_endpoint(websocket: WebSocket):

    protocols = websocket.headers.get(
        "sec-websocket-protocol",
        ""
    )

    print("Protocol:", protocols)

    if "ocpp1.6" not in protocols:

        print("Protocollo OCPP mancante")

        await websocket.close()

        return

    await websocket.accept(
        subprotocol="ocpp1.6"
    )

    print("Wallbox collegata")

    connection = WebSocketAdapter(
        websocket
    )

    cp = CP(
        "ENSTO001",
        connection
    )

    try:

        await cp.start()

    except WebSocketDisconnect:

        print(
            "Wallbox disconnessa"
        )
