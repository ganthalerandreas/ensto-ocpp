from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call_result
from ocpp.routing import on

from app.database import SessionLocal
from app.models import ChargingSession

import datetime


PRICE_PER_KWH = 0.30  # modificabile

class ChargePointHandler(CP):

    async def run(self):
        await self.start()

    @on("BootNotification")
    async def boot(self, **kwargs):

        return call_result.BootNotification(
            current_time=datetime.datetime.utcnow().isoformat(),
            interval=30,
            status="Accepted"
        )

    @on("StartTransaction")
    async def start(self, meter_start, timestamp, **kwargs):

        db = SessionLocal()

        session = ChargingSession(
            start_time=timestamp,
            meter_start=meter_start,
            status="Charging"
        )

        db.add(session)
        db.commit()

        return call_result.StartTransaction(transaction_id=session.id)

    @on("StopTransaction")
    async def stop(self, transaction_id, meter_stop, timestamp, **kwargs):

        db = SessionLocal()

        session = db.query(ChargingSession).filter_by(id=transaction_id).first()

        session.end_time = timestamp
        session.meter_stop = meter_stop

        kwh = (meter_stop - session.meter_start) / 1000
        session.energy_kwh = kwh
        session.total_euro = kwh * PRICE_PER_KWH
        session.status = "Completed"

        db.commit()

        print("RICARICA COMPLETATA:", session.total_euro)

        return call_result.StopTransaction()
