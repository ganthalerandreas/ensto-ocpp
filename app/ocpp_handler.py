from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call_result
from ocpp.routing import on
import datetime


class ChargePointHandler(CP):

    async def run(self):
        await self.start()

    @on("BootNotification")
    async def boot(self, **kwargs):

        print("Wallbox connessa")

        return call_result.BootNotification(
            current_time=datetime.datetime.utcnow().isoformat(),
            interval=30,
            status="Accepted"
        )

    @on("StatusNotification")
    async def status(self, **kwargs):

        print("Status ricevuto")

        return call_result.StatusNotification()

    @on("StartTransaction")
    async def start(self, **kwargs):

        print("Ricarica iniziata")

        return call_result.StartTransaction(transaction_id=1)

    @on("StopTransaction")
    async def stop(self, **kwargs):

        print("Ricarica terminata")

        return call_result.StopTransaction()
