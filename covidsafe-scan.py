# Australian COVIDSafe App Scanner
# (c) Alwen Tiu, 2020
#
# A simple bluetooth scanner to query phones running the Australian COVIDSafe App. 

import logging
import argparse
from bluepy.btle import *
from bluepy.btle import BTLEException, BTLEDisconnectError
import json
from datetime import datetime
import base64
import binascii 

# Separate components of v2 message payload for writing into csv file.
def decodepayload(msgstring, versionNum) :
  hexstring = base64.b64decode(msgstring).hex()

  if(versionNum == 2) :
    # first check min possible length
    if(len(hexstring) < 166) : 
      print("Error decoding v2 payload: msg too short.\n")
    else :
    # Comma-separate 1-byte pubkey y (compressed), 32-byte pubkey x, 2-byte counter, 
    # >= 16-byte ciphertext, 16-byte HMAC
      hexstring = hexstring[0:2]+","+hexstring[2:66]+","+hexstring[66:70]+","\
                  +hexstring[70:-32]+","+hexstring[-32:]
  elif(versionNum != 1) :
    print("Error decoding payload: don't recognise version "+versionNum+"\n") 

  return hexstring+"\n"

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            logging.info("Discovered device " + dev.addr)
        elif isNewData:
            logging.info("Received new data from " +dev.addr)

parser = argparse.ArgumentParser()
parser.add_argument('--timeout', dest='tm', type=int, default=15, help='scanner timeout in seconds')
parser.add_argument('--rssi', dest='rssi', type=int, default=-85, help='RSSI threshold (default -85 dBm)')
parser.add_argument('--mtu', dest='mtu', type=int, default=512, help='MTU (default 512)')
parser.add_argument("--decodepayload", help="separate v2 msg parts in payload.csv",
                    action="store_true")

args = parser.parse_args()

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s',
        filename='covidsafe.log',
        filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger('').addHandler(console)

print("Scanning (timeout " + str(args.tm) + " seconds, RSSI threshold: " + str(args.rssi) + ")")
scanner = Scanner().withDelegate(ScanDelegate())
fail=True
while fail:
  try:
    devices = scanner.scan(args.tm)
    fail=False
  except BTLEDisconnectError:
    print("Device disconnected. Retrying... (Ctrl-C to cancel)\n")
  except:
    print("Scan error")
    exit()

# COVIDSafe advertises its service using the following UUID
uuid="b82ab3fc-1595-4f6a-80f0-fe094cc218f9"

# see https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/ 
# for the numeric code used in getDescription/getValueText

with open("payload.csv", "a") as pf:
  for dev in devices:
   try:
     svc_val=dev.getValueText(7)
     svc_desc=dev.getDescription(7)
     if(svc_val == uuid and dev.rssi >= args.rssi):
       logging.info("===============================================================")
       logging.info("Device " + dev.addr + " (" + dev.addrType + "), RSSI=" + str(dev.rssi) + " dB")
       nm_desc = dev.getDescription(9)
       nm_val = str(dev.getValueText(9))
       mnf_desc = dev.getDescription(255)
       mnf_val  = str(dev.getValueText(255))
       logging.info(nm_desc + " = " + nm_val)
       logging.info(mnf_desc + " = " +  mnf_val)
       logging.info(svc_desc + " = " +  svc_val)
       p = Peripheral(dev)
       p.setMTU(args.mtu)
       c=p.getCharacteristics(1,0xffff,uuid)
       s=(c[0].read()).decode("utf-8")
       j=json.loads(s)
       ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
       # Save to payload.csv
       # Columns: timestamp, device address, device type, rssi, model, version, message
       row=ts+","+dev.addr + "," + dev.addrType + "," + str(dev.rssi) 
       row=row+","+j['modelP']+","+ str(j['v'])
       if(args.decodepayload) :
         msgstring = decodepayload(j['msg'], j['v']) 
       else :
         msgstring=j['msg'].replace("\/","/").replace("\n","") 
       row=row+","+msgstring+"\n"
       pf.write(row)
       logging.info("Payload: \n" + s)
       p.disconnect()
   except BTLEException:
     logging.info("Error connecting to or reading from device " + dev.addr)
     

