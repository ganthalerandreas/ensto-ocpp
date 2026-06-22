import asyncio
import websockets

from ocpp.v16 import ChargePoint
from ocpp.v16 import call_result
from ocpp.routing import on


class CP(ChargePoint):

    @on("BootNotification")
    async def on_boot(self, **kwargs):
        return call_result.BootNotification(
            current_time="2026-01-01T00:00:00Z",
            interval=30,
            status="Accepted"
        )


async def handler(websocket):

    # IMPORTANTISSIMO: accetta subprotocol manualmente
    cp_id = "ENSTO001"

    cp = CP(cp_id, websocket)

    await cp.start()


async def main():

    async def ws_handler(websocket, path=None):

        # accetta SOLO se subprotocol OCPP è presente
        if websocket.subprotocol != "ocpp1.6":
            print("SUBPROTOCOL ERRATO:", websocket.subprotocol)
            await websocket.close()
            return

        await handler(websocket)

    server = await websockets.serve(
        ws_handler,
        "0.0.0.0",
        8765,
        subprotocols=["ocpp1.6"]
    )

    print("OCPP SERVER RUNNING")
    await server.wait_closed()


asyncio.run(main())
