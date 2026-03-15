import os
import asyncio
import logging
import json
import time

from meshcore import MeshCore, EventType

from lib import config_lib
from lib import serial_lib

logging.basicConfig(filename="mc_logfile.log",
                    format='%(asctime)s %(levelname)s: %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dirPath = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(dirPath, "mc_config.json")
config = config_lib.Config(configPath=configPath, logger=logger)
serial = serial_lib.Serial_helper(pid=config.getUsbPid(), vid=config.getUsbVid())

serial.listPorts()
print("port:", serial.getUsbPort())

async def saveContacts(): 
    mc = await MeshCore.create_serial(serial.getUsbPort(), auto_reconnect=True, max_reconnect_attempts=5)

    result = await mc.commands.get_contacts()
    if result.type == EventType.ERROR:
        print(f"Error getting contacts: {result.payload}")
        return 0
    contacts = result.payload
    print(f"Found {len(contacts)} contacts")

    contactList = list()
    for i in contacts:
        #if "KT" in contacts[i]['adv_name']:
            #print(contacts[i])
        aa = mc.get_contact_by_name(contacts[i]['adv_name'])
        contactList.append(aa)



    with open("contacts.jsonl", "w") as file:
        for i in contactList:
            file.write(json.dumps(i))
            file.write("\n")


async def main():
    global mc
    mc = await MeshCore.create_serial(serial.getUsbPort(), auto_reconnect=True, max_reconnect_attempts=5)

    await saveContacts()

    await mc.disconnect()

if __name__ == "__main__":
    asyncio.run(main())