#!/usr/bin/env python
import asyncio
import os

import uvicorn
from kimera.Bootstrap import Bootstrap
from kimera.comm.Intercom import Message
from kimera.helpers.Helpers import Helpers
from kimera.process.Spawner import Spawner

# from app.ext.bots.discord.run import jolly_run

Helpers.sysPrint("BOOTING: ", os.getenv("TAG"))



async def start_services():
    Helpers.sysPrint("START","SERVICES")

    boot = Bootstrap(True)
    # Start Redis subscription
    # Spawner().start("roco", jolly_run)
    #Spawner().loop("binGram", WorkBinGram().start,{},True)
    #
    # async def socket(message,event,room,head,final=False):
    #     await boot.api.socket(message=message, event=event, room=room, head=head, final=final)

    async def socket(message):
        Helpers.print(message)
        await boot.api.socket(**message)

    if boot.api_on:
        Helpers.sysPrint("API", "ON")

        await boot.run_intercom("sio", socket)


        config = uvicorn.Config(boot.api.app, host="0.0.0.0", port=8000,log_level="warning")
        server = uvicorn.Server(config)
        # Run Uvicorn server asynchronously
        await server.serve()
    else:
        Helpers.sysPrint("API", "OFF")
        while True:
            await asyncio.sleep(1)



if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except Exception as e:
        print(e)
        Helpers.errPrint("ERROR ON STARTUP")
