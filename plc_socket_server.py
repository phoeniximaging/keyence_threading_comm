# echo-server.py

'''
Ritesh wants to see the C# implementation in place. 
Since my current PLC api still has a problem reading .O bools I need you to modify your plc server to just read the .O signals from the PLC. 
* Write it as a socket server to listen on 127.0.0.1:4000 for robot 2 requests and 127.0.0.1:4001 for robot 3 read requests. *
I'm using different sockets to keep the communications simple. Request format will be simply a text string "read\n".

When you get a read request, read the signals from the plc for the corresponding robot and put the result into a dictionary. 
Use the same format as in your test program with the last part of the tag name as the key and the result should be a bool (True | False). 
Use json.dumps(<dictionary>) to serialize the dictionary and return the serialized string terminated with "\n".

'''

import socket
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import json
import threading

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 4000  # Port to listen on (non-privileged ports are > 1023)

# global variable declarations, some are probably unnecessary(?)
arrayOutTags = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(machine_num, plc):
    #print("read_plc_dict, generating list of read tags")
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.O.' + tag;
        #print(newTag);
        readList.append(newTag)
        
    resultsList = plc.read(*readList) # tag, value, type, error
    readDict = {}

    for tag in resultsList:
        key = tag.tag.split(".")[-1]
        readDict[key] = tag[1]

    #print(readDict)
    return readDict
#END read_plc_dict

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        print(f'({host}):({port}) Alive and listening!\n')
        print(f'({host}):({port}) Connecting to PLC...\n')
        with LogixDriver('120.123.230.39/0') as plc:
            print(f'({host}):({port}) Connected to PLC!\n')
            while True:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"({host}):({port}) Connected by {addr}\n")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        #print(f'{type(data)}')
                        #conn.sendall(data)
                        #test_obj = {"key": "value"}
                        #test_obj_json = json.dumps(test_obj)
                        plc_result = {}
                        if(port == 4000):
                            plc_result = read_plc_dict('1', plc)
                        elif(port == 4001):
                            plc_result = read_plc_dict('2', plc)
                        else:
                            print('Invalid Server Port! Should be : 4000 or 4001')
                        plc_result_json = json.dumps(plc_result)
                        conn.sendall(plc_result_json.encode())

def main():
    # Thread declaration / initialization
    t1 = threading.Thread(target=start_server, args=["127.0.0.1", 4000])
    t2 = threading.Thread(target=start_server, args=["127.0.0.1", 4001])
    #start_server(HOST, PORT)

    t1.start()
    t2.start()

    t1.join()
    pass

#implicit 'main()' declaration
if __name__ == '__main__':
    while(True):
        main()