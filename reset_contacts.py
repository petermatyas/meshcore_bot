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




async def login(mc, repeater, password, retry=3):
    login_ok = False

    while retry > 0 and not login_ok:
        #print(f"login trial {3-retry+1}")
        #print(f"retry: {retry}   login_ok: {login_ok}   {retry > 0} {not login_ok}")
        retry -= 1 

        login_cmd = await mc.commands.send_login(repeater, password)
        if login_cmd == None:
            #print("Error send login command")
            continue
        elif login_cmd.type == EventType.ERROR:
            #print(f"Login error: {login_cmd}")
            logger.error(f"{repeater} login error: {login_cmd}")
            continue
        else:
            login_cmd_resp = await mc.wait_for_event(EventType.LOGIN_SUCCESS, timeout=20)
            if login_cmd_resp == None:
                print(f"login timeout error: {repeater["adv_name"]}")
                continue
            elif login_cmd_resp.type == EventType.ERROR:
                print("login_cmd_resp", login_cmd_resp) 
                continue
            else:
                print(f"login succes: {repeater["adv_name"]}")
                login_ok = True
                return True
    return False

async def setTime(adv_name, password):
    print(f"adv_name: {adv_name}")
    contact = mc.get_contact_by_name(adv_name)

    if contact == None:
        logger.error(f"no contact: {adv_name}")
        return 
    
    res = await login(adv_name, password)
    if res:
        ts = int(time.time())
        res = await mc.commands.set_time(ts)




async def resetAllContacts(): 
    mc = await MeshCore.create_serial(serial.getUsbPort(), auto_reconnect=True, max_reconnect_attempts=5)


    result = await mc.commands.get_contacts()
    if result.type == EventType.ERROR:
        print(f"Error getting contacts: {result.payload}")
        return 0
    contacts = result.payload
    print(f"Found {len(contacts)} contacts")


    for public_key in contacts:
        name = mc.get_contact_by_name(contacts[public_key]['adv_name'])

        result = await mc.commands.remove_contact(public_key)
        if result.type == EventType.ERROR:
            print(f"Error remove contact: {name} {result.payload}")





async def main():
    global mc
    mc = await MeshCore.create_serial(serial.getUsbPort(), auto_reconnect=True, max_reconnect_attempts=5)

    await resetAllContacts()

    await mc.disconnect()

asyncio.run(main())
#asyncio.run(saveContacts())




