# Python - PLC to Keyence Middleman

## Code
This code reads values from an Allen-Bradley Logix PLC to load and trigger a Keyence unit. Also writes out result files (alongside the Keyence unit itself). Requires a "config.txt" file to designate IP addresses.

### Setup:
I created this in Visual Studio Code, Python 3.9.5

#### Description:
```
import pycomm3
import threading
import datetime, time
import socket
import json
```

Uses the open-source pycomm3 library to communicate with the PLC.
Uses multiple threads to concurrently run multiple Keyence units at once (with separate sets of PLC tags).
Uses datetime/time for error detection and performance logging.
Uses socket to connect and interact with the Keyence unit(s)
Uses json to load in a config file, for IP addressing mainly

## main.py:
All the functional code is in this file. Requires a companion 'config.txt' file to designate addresses.

Connects to the PLC, connects to the Keyence unit(s), then listens for the proper tags with the proper values to start stepping through the timing diagram. Utilizes two dedicated "heartbeat" threads that will write back to the PLC to ensure we are actively connected.

## Other files
Other files here are from various tests built along the way. They are NOT required to run the platform and work through the timing diagram.