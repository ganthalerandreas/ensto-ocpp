from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import asyncio
import datetime
import websockets

from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call_result
from ocpp.routing import on

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


async def on_connect(websocket):

    if websocket.subprotocol != "ocpp1.6":

        print(
            "Subprotocol errato:",
            websocket.subprotocol
        )

        await websocket.close()

        return

    cp = ChargePointHandler(
        "ENSTO001",
        websocket
    )

    print("Wallbox collegata")

    await cp.start()


async def run_ocpp_server():

    server = await websockets.serve(
        on_connect,
        "0.0.0.0",
        9000,
        subprotocols=["ocpp1.6"]
    )

    print("OCPP server avviato")

    await server.wait_closed()


@app.on_event("startup")
async def startup():

    asyncio.create_task(
        run_ocpp_server()
    )


@app.get("/")
def home():

    return HTMLResponse(f"""
    <html>
    <body>

    <h1>Wallbox Status</h1>

    <h2>{current_status}</h2>

    </body>
    </html>
    """)
