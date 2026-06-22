import asyncio
import datetime
import json
import websockets

from ocpp.v16 import ChargePoint
from ocpp.v16 import call_result
from ocpp.routing import on

from app.database import get_session
from app.models import ChargingSession
from app.emailer import send_email

PRICE_PER_KWH = 0.30

active_sessions = {}


class CP(ChargePoint):

    @on("BootNotification")
    async def on_boot(self, **kwargs):
        return call_result.BootNotification(
            current_time=datetime.datetime.utcnow().isoformat(),
            interval=30,
            status="Accepted"
        )

    @on("StatusNotification")
    async def on_status(self, status, **kwargs):
        print("STATUS:", status)
        return call_result.StatusNotification()

    @on("StartTransaction")
    async def on_start(self, id_tag, meter_start, timestamp, **kwargs):

        db = get_session()

        session = ChargingSession(
            start_time=timestamp,
            meter_start=meter_start,
            status="Charging"
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        active_sessions[self.id] = session.id

        return call_result.StartTransaction(transaction_id=session.id)

    @on("StopTransaction")
    async def on_stop(self, transaction_id, meter_stop, timestamp, **kwargs):

        db = get_session()

        session = db.query(ChargingSession).filter_by(id=transaction_id).first()

        session.end_time = timestamp
        session.meter_stop = meter_stop

        kwh = (meter_stop - session.meter_start) / 1000
        session.energy_kwh = kwh
        session.total_euro = kwh * PRICE_PER_KWH
        session.status = "Completed"

        db.commit()

        send_email(session)

        return call_result.StopTransaction()


async def handler(websocket, path):

    cp_id = path.split("/")[-1]

    cp = CP(cp_id, websocket)

    await cp.start()


async def start_ocpp_server():

    server = await websockets.serve(
        handler,
        "0.0.0.0",
        8765,
        subprotocols=["ocpp1.6"]
    )

    print("OCPP Server started")
    await server.wait_closed()
