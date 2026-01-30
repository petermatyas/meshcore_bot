import sys
import json
import csv
import time
import os
import requests
import logging
from datetime import datetime 

from dotenv import load_dotenv

import asyncio
from meshcore import MeshCore, EventType

from lib import influx_lib
from lib import serial_lib
from lib import db
from lib import config_lib
from lib import chatbot_lib


load_dotenv()

logging.basicConfig(filename="mc_logfile.log",
                    format='%(asctime)s %(levelname)s: %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



chatbot = chatbot_lib.Chatbot()
db = db.Db()


dirPath = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(dirPath, "mc_config.json")
config = config_lib.Config(configPath=configPath, logger=logger)

serial = serial_lib.Serial_helper(pid=config.getUsbPid(), vid=config.getUsbVid())

async def sendMessage(contact, message):
    
    result = await mc.commands.send_msg(contact, message)
    print("result", result)
    if result.type == EventType.ERROR:
        print(f"⚠️ Failed to send message: {result.payload}")
    expected_ack = result.payload["expected_ack"].hex()
    print(f"Message sent, waiting for ACK with code: {expected_ack}")
    
    timeout=15
    # Wait for the specific ACK that matches our message
    ack_event = await mc.wait_for_event(
        EventType.ACK,
        #attribute_filters={"code": expected_ack},
        timeout=timeout
    )
    print("ack_event", ack_event)
    
    if ack_event:
        print(f"✅ Message confirmed delivered! (ACK received)")
    else:
        print(f"⚠️ Timed out waiting for ACK after {timeout} seconds")  
    


async def getRemoteLocation(nodeName):
    repeater = mc.get_contact_by_name(nodeName)
    if repeater == None:
        return "Node is not in database, send advert"
    res = await getTelemetry(mc, repeater)
    if res["status"] == "ok":
        return res["payload"]

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

async def check_coordinates():
    while True:
        #print("Requesting battery level...")

        trackers = chatbot.getTrackers()
        for adv_name in trackers:
            #print(i)
            last_time  = trackers[adv_name]["last_time"]
            interval   = trackers[adv_name]["interval"]
            now        = time.time()

            if time.time() - last_time > interval:
                telemetry = await getRemoteLocation(adv_name)

                for i in telemetry:
                    if i["type"] == "gps":
                        lat = i["value"]["latitude"]
                        lon = i["value"]["longitude"]
                        alt = i["value"]["altitude"]

                        if lat != trackers["adv_name"]["last_latitude"] and \
                           lon != trackers["adv_name"]["last_longitude"]:
                            db.savePosition(adv_name, lat, lon, alt)
                
                trackers[i]["last_time"] = now


        #await mc.commands.get_bat()  # This command will trigger a battery event
        await asyncio.sleep(1)        

def processStatus(status):
    blackList = ["pubkey_pre"]
    res = dict()
    for key, value in status.items():
        if key not in blackList:
            res[key] = value
    return res

def processTelemetry(telemetry):
    res = dict()
    for i in telemetry:
        if i["type"] == "temperature" and i["value"] > 45:
            #chanel = i["channel"]
            value = i["value"]
            res["cpu_temperature"] = value
            #temp.append({"channel":chanel, "type":"cpu_temperature", "value":value})
        else:
            res[i["type"]] = i["value"]
            #temp.append(i)
    return res

async def getTelemetry(nodeName):
    logger.info(f"telemetry request: {nodeName}")

    await mc.ensure_contacts()
    contact = mc.get_contact_by_name(nodeName)
    if contact == None:
        #logger.debug(f"Node {nodeName} is not in database, send advert")
        raise Exception(f"Unknown node: {nodeName}")
    logger.debug(f"contact: {contact}")

    telemetry_req = await mc.commands.send_telemetry_req(contact)
    if telemetry_req.type == EventType.ERROR:
        logger.debug("Error sending telemetry request:", telemetry_req)
        raise Exception(f"Telemetry req error: {telemetry_req}")
    #logger.debug(f"telemetry_req: {telemetry_req}")

    suggested_timeout = telemetry_req.payload["suggested_timeout"] / 800
    logger.debug(f"{nodeName} timeout: {suggested_timeout}")
    suggested_timeout = 20

    telemetry_event = await mc.wait_for_event(EventType.TELEMETRY_RESPONSE, timeout=suggested_timeout)  
    if telemetry_event == EventType.ERROR:
        #logger.debug(telemetry_event)
        raise Exception(telemetry_event)

    logger.debug(f"telemetry_event: {telemetry_event}")

    if not hasattr(telemetry_event, "payload"):
        raise Exception("telemetry timeout")

    if not "lpp" in telemetry_event.payload:
        raise Exception("no valid telemetry data")    
    
    return telemetry_event.payload["lpp"]

async def getStatus(nodeName):
    await mc.ensure_contacts()
    contact = mc.get_contact_by_name(nodeName)
    if contact == None:
        #logger.debug(f"Node {nodeName} is not in database, send advert")   
        raise Exception("unknown node")
    
    status_req = await mc.commands.send_statusreq(contact)
    if status_req.type == EventType.ERROR:
        #logger.debug("Error sending status request:", status_req)
        raise Exception(status_req) 

    #suggested_timeout = status_req.payload["suggested_timeout"]

    status_event = await mc.wait_for_event(EventType.STATUS_RESPONSE, timeout=10)
    if status_event == EventType.ERROR:
        #logger.debug(status_event)
        raise Exception(status_event)
    elif status_event == None:
        #logger.debug("Status request timeout")
        raise Exception("timeout")

    status = processStatus(status_event.payload)
    return status

async def check_repeater_telemetry():
    while True:
        sensorNodes = config.getTelemetryList()


        for node in sensorNodes:
            nodeName = node["adv_name"]

            if config.isQuery(nodeName, "telemetry"):
                if config.isQueryTrigger(nodeName, "telemetry"):
                    config.queryTriggered(nodeName, "telemetry")
                    try:       
                        telemetry_raw = await getTelemetry(nodeName)
                        telemetry = processTelemetry(telemetry_raw)

                        logger.info(f"{nodeName} telemetry")
                        influx_lib.write_influx(measurement="telemetry", tags=telemetry, fileds={"node":nodeName})
                    except Exception as e:
                        logger.warning(f"Error getting telemetry for {nodeName}: {e}")
                #else:
                #    print(f"telemetry {nodeName} diff time: {time.time() - config.queryIntervals[nodeName]['telemetry']}, interval: {config.getQueryInterval(nodeName, 'telemetry')}")

            if config.isQuery(nodeName, "status"):
                if config.isQueryTrigger(nodeName, "status"):  
                    config.queryTriggered(nodeName, "status")
                    try:  
                        status_raw = await getStatus(nodeName)
                        status = processStatus(status_raw)

                        logger.info(f"{nodeName} status")
                        influx_lib.write_influx(measurement="status", tags=status, fileds={"node":nodeName})
                    except Exception as e:
                        logger.warning(f"Error getting status for {nodeName}: {e}")
                    

        await asyncio.sleep(10)

async def handlePrivMessage(event):
    data = event.payload
    #db.saveMessage(data)

    logger.info(f"New message received: {data}")

    __messageSplitted = data["text"].lower().split(" ")
    command = __messageSplitted[0]
    params  = __messageSplitted[1:]
    contact = mc.get_contact_by_key_prefix(data['pubkey_prefix'])
    adv_name = contact["adv_name"]
    try:
        adv_lat = contact["adv_lat"]
        adv_lon = contact["adv_lon"]
    except:
        adv_lat = None
        adv_lon = None

    adv_name, answer = await chatbot.parse(command, params, adv_name, adv_lat, adv_lon)

    if adv_name != None and answer != None:
        #print("answer:", answer)
        contact =  mc.get_contact_by_name(adv_name)
        if not contact:
            logger.info(f"no {adv_name} contact")
        #print("contact", contact)
        await sendMessage(contact, answer)

async def handleChanMessage(event):
    """
    {'type': 'CHAN', 'channel_idx': 0, 'path_len': 0, 'txt_type': 0, 'sender_timestamp': 1769631085, 'text': 'ha1mp: Test'}
    """
    data = event.payload

    channel_idx = data["channel_idx"]
    adv_name = data["text"].split(":")[0]
    msg = data["text"].split(":")[1].strip()
    command = msg.split(" ")[0]
    params  = msg.split(" ")[1:]
    contact = mc.get_contact_by_name(adv_name)
    try:
        adv_lat = contact["adv_lat"]
        adv_lon = contact["adv_lon"]
    except:
        adv_lat = None
        adv_lon = None

    adv_name, answer = await chatbot.parse(command, params, adv_name, adv_lat, adv_lon)
    
    result = await mc.commands.send_chan_msg(channel_idx, answer)
    if result.type == EventType.ERROR:
        print(f"Error sending reply: {result.payload}")
    else:
        print("Reply sent")

async def saveContacts():
    while True:
        result = await mc.commands.get_contacts()
        if result.type == EventType.ERROR:
            print(f"Error getting contacts: {result.payload}")
        else:
            payload = result.payload
            payload
            json_str = json.dumps(payload, indent=4)
            with open(config.getContactSaveFilename(), "w") as f:
                f.write(json_str)

        await asyncio.sleep(config.getContactSaveInterval())


async def removePaths(adv_names):
    for adv_name in adv_names:
        contact = mc.get_contact_by_name(adv_name)
        if contact:
            public_key = contact["public_key"]

            result = await mc.commands.reset_path(public_key)
            if result.type == EventType.ERROR:
                logging.info(f"Error remove path: {result.payload}")
            else:
                logging.info(f"Path removed: {adv_name}")

            """
            result = await mc.commands.send_path_discovery(contact)
            if result.type == EventType.ERROR:
                logging.info(f"Error path discovery: {result.payload}")
            
            event = await mc.wait_for_event(
                EventType.MSG_SENT,
                timeout=15
            )
            print("send path dicovery event", event)

            if event:
                print("====>>>", event.payload)
            """


            path = config.getPathByName(adv_name)
            if path != None:
                print()
                result = await mc.commands.change_contact_path(contact, path)
                if result.type == EventType.ERROR:
                    logging.info(f"Error add path: {result.payload}")
                else:
                    logging.info(f"Path ({path}) added to {adv_name}")


async def main():
    global mc

    mc = await MeshCore.create_serial(serial.getUsbPort(), auto_reconnect=True, max_reconnect_attempts=5)

    if mc.is_connected:
        logging.info("Serial connection estabilished")

    #channel settings
    for chan in config.getChannels():
        channel_idx = chan["index"]
        channel_name = chan["name"]
        secret_key = chan["secret_key"]

        #try:
        channel_secret = bytes.fromhex(secret_key)
        #except ValueError:
        #    print("Error: Invalid hex string")
        #    return

        print(f"Setting channel {channel_idx}...")
        result = await mc.commands.set_channel(channel_idx, channel_name, channel_secret)

        if result.type == EventType.OK:
            print("Channel configured successfully!")
        elif result.type == EventType.ERROR:
            print(f"Error setting channel: {result.payload}")
        else:
            print(f"Unexpected response: {result.type}")

    await mc.ensure_contacts()
    await mc.start_auto_message_fetching()

    adv_names = [i["adv_name"] for i in config.getTelemetryList()]
    await removePaths(adv_names)

    # Subscribe to private messages
    private_subscription = mc.subscribe(EventType.CONTACT_MSG_RECV, handlePrivMessage)
    channel_subscription = mc.subscribe(EventType.CHANNEL_MSG_RECV, handleChanMessage)

    
    

    try:
        #task = asyncio.create_task(check_coordinates())
        task2 = asyncio.create_task(check_repeater_telemetry())
        task_contact = asyncio.create_task(saveContacts())

        while True:
            line = (await asyncio.to_thread(sys.stdin.readline)).rstrip('\n')

    except KeyboardInterrupt:
        mc.stop()
        print("\nExiting...")
    except asyncio.CancelledError:
        # Handle task cancellation from KeyboardInterrupt in asyncio.run()
        print("\nTask cancelled - cleaning up...")
    finally:
        # Clean up subscriptions
        mc.unsubscribe(private_subscription)
        mc.unsubscribe(channel_subscription)
    
        # Stop auto-message fetching
        await mc.stop_auto_message_fetching()
    
        # Disconnect
        await mc.disconnect()


if __name__ == "__main__":    

    asyncio.run(main())
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExited cleanly")
    except Exception as e:
        print(f"Error: {e}")
    """