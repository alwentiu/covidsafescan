# A simple COVIDSafe app scanner
Alwen Tiu, 2020

This script scans for phones running the Australian COVIDSafe app and displays the payload. 

## System requirements

This has been tested in Ubuntu 18.04 LTS, running the Bluez protocol stack. It uses the bluepy python library. You may need to install the bluepy library. Here is a short instruction; for details see [https://github.com/IanHarvey/bluepy](https://github.com/IanHarvey/bluepy):

> sudo apt install python3-pip libglib2.0-dev

> sudo pip3 install bluepy

## Running the script

You may want to run the setup.sh script first to turn on bluetooth and change some settings of the bluetooth daemon. I find that setting the 'privacy' option on (which will randomise the MAC addresses of the scanning device) makes the scanner works more reliably. This setup needs to be done only once per scanning session. 

> chmod a+x setup.sh

> sudo ./setup.sh

The actual scanner is in the covidsafe-scan.py script. To run the script:

> sudo python3 covidsafe-scan.py

The output of the scan will be displayed on the screen and also saved to the file **covidsafe.log**. The payload of the scan is saved to the file **payload.csv**.

## Options

### Decode payload
To receive the payload in **payload.csv** in hex, and, for v.1.0.18, deomposed into its component parts
(public key y, public key x, counter, ciphertext, HMAC), use:

> sudo python3 covidsafe-scan.py --decodepayload

### Scanning timemout

If you see a scan error message, you may want to increase the scan timeout (the default is 15 seconds). For example, to increase the timeout to 30 seconds, use the following command:

> sudo python3 covidsafe-scan.py --timeout 30


### RSSI threshold

The default RSSI threshold (roughly, signal strength of the bluetooth devices to be scanned) is set to -85 dBm. You can specify a different threshold using the --rssi option, e.g.,

> sudo python3 covidsafe-scan.py --rssi -70

sets the threshold to -70 dBm. 

#### MTU size

The default MTU (Maximum Transmission Unit) is set to 512, which is the maximum allowed length. You can set it to a smaller value if you experiencing issues with unreliable payload download. For example,

>sudo python3 covidsafe-scan.py --mtu 256

sets the MTU to 256. 

## Limitation

This scanner can detect the Android version of COVIDSafe either in the foreground or in the background. But for the iOS version, it works reliably only when the app is running in the foreground.

It has been tested for COVIDSafe Android up to v1.0.18, and COVIDSafe iOS up to v1.4.


