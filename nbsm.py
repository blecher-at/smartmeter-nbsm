#!/usr/bin/python3
from Cryptodome.Cipher import AES
import argparse
import binascii
import serial
import datetime
import json
import requests
import time
import configargparse

# CONFIG PART



# END CONFIG PART

# parse command line parameeters to see which libraries are needed

parser = configargparse.ArgParser(default_config_files=['/etc/nbsm.conf', '~/.nbsm'])
parser.add('-c', '--config', required=False, is_config_file=True, help='config file path')
parser.add("-m", "--mode", help="The publish mode", choices=["stdout","json", "mqtt"], required=True)
parser.add("-v", "--verbose", help="print verbose messages", action='store_true')
parser.add("--encryption-key", help="the encryption key you've got from Netz Burgenland. This is not the auth_key, which is not needed at all", required=True)
args, extra_args = parser.parse_known_args()

if (args.mode == "json"):
    import requests
    parser.add("--json-endpoint", help="if the publish mode is json, configure the http(s) endpoint here", required=True)
    args = parser.parse_args()

elif (args.mode == "mqtt"):
    import paho.mqtt.client as mqtt
    parser.add("--mqtt-server", help="if the publish mode is mqtt, configure the mqtt server", required=True)
    parser.add("--mqtt-topic", help="if the publish mode is mqtt, configure the mqtt topic", required=True)
    parser.add("--mqtt-user", help="if the publish mode is mqtt, configure the mqtt username")
    parser.add("--mqtt-password", help="if the publish mode is mqtt, configure the mqtt password")
    args = parser.parse_args()


cfgEncKey = args.encryption_key
encKey = bytearray(binascii.unhexlify(cfgEncKey))

def decrypt_msg(readdata):

    LandisDataSize = 111
    LandisHDCLHeaderSize = 13
    
    systitle = readdata[LandisHDCLHeaderSize + 1:LandisHDCLHeaderSize + 1 + 8] # 8 bytes
    nonce = readdata[LandisHDCLHeaderSize + 11:LandisHDCLHeaderSize + 11 + 4]  # 4 bytes

    initvec = systitle + nonce

    cipher = AES.new(encKey, AES.MODE_GCM, initvec)
    plaintxt = cipher.decrypt(readdata[LandisHDCLHeaderSize + 15:-3])

    #print("process: ", plaintxt.hex())
    Year = int.from_bytes(plaintxt[6:8], "big") 
    Month = plaintxt[8]
    Day = plaintxt[9]
    Hour = plaintxt[11]
    Minute = plaintxt[12]
    Second = plaintxt[13]

    i = 35
    p = int.from_bytes(plaintxt[35:39], "big") 
    r2 = int.from_bytes(plaintxt[40:44], "big") 
    r3 = int.from_bytes(plaintxt[45:49], "big") 
    r4 = int.from_bytes(plaintxt[50:54], "big") 
    w = int.from_bytes(plaintxt[55:59], "big") 
    r5 = int.from_bytes(plaintxt[60:64], "big") 
    r6 = int.from_bytes(plaintxt[65:69], "big") 
    
    jsdata = {}
    jsdata["datetime"] = datetime.datetime(Year, Month, Day, Hour, Minute, Second).isoformat()

    jsdata["current_w"] = w
    jsdata["total_wh"] = p
    jsdata["L1"] = {}
    jsdata["L1"]["r2"] = r2
    jsdata["L1"]["r3"] = r3
    jsdata["L1"]["r4"] = r4
    jsdata["L1"]["r5"] = r5
    jsdata["L1"]["r6"] = r6
    

    if (args.mode == "stdout"):
        print(json.dumps(jsdata))
    elif (args.mode == "json"):
        # if the publish mode is json, configure the http(s) endpoint here
        cfgJsonEndpoint = args.json_endpoint
        requests.post(cfgJsonEndpoint, json=jsdata)
    elif (args.mode == "mqtt"):
        publish_mqtt(jsdata)

def publish_mqtt(jsdata):
    client = mqtt.Client("nbsm")
    
    # if the publish mode is mqtt, configure the mqtt variables here
    cfgMqttServer = args.mqtt_server
    cfgMqttUser = args.mqtt_user
    cfgMqttPassword = args.mqtt_password
    cfgMqttMainTopic = args.mqtt_topic

    if (args.verbose):
        print (args)

    if (len(cfgMqttUser) > 0):
        client.username_pw_set(username=cfgMqttUser, password=cfgMqttPassword)

    client.connect(cfgMqttServer)

    client.publish(cfgMqttMainTopic + "status/datetime", jsdata["datetime"])
    client.publish(cfgMqttMainTopic + "status/current_w", jsdata["current_w"])
    client.publish(cfgMqttMainTopic + "status/total_wh", jsdata["total_wh"])

### main ###
tty = serial.Serial(port='/dev/ttyUSB0', baudrate = 9600, parity =serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

data = bytearray()

while True:
    while tty.in_waiting > 0:
        readidx = len(data)
        b = tty.read()
        data += b
        #print(b.hex(), end='', flush=True)
        #print(" ", readidx)

        startpos = data.find(b'\x7e\xa0')

        if (startpos >= 0):
            # found start position. calc corrected idx within the message
            idx = readidx - startpos
            if (idx == 2):
                totallen = data[readidx]
                data += tty.read(totallen - 1) #-1: length is already included
                #print("process: ", data[startpos:].hex())
                decrypt_msg(data[startpos:])
                data = bytearray()

    time.sleep(0.1)

