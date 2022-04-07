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

kill_threads = False

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
    tagKeys.append(tag.split("{")[0]) # delete trailing { if it exists

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

def read_plc_tag(plc, tag):
    read_plc = plc.read(tag)
    read_plc_value = str(read_plc[1])
    return read_plc_value
#END read_plc_tag

# starts up server(s), listens for requests, reads appropriate tags then returns results as serialized json string
def start_server(host, port):
    global kill_threads # thread health boolean, if 'True' time to end threads

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        print(f'({host}):({port}) Alive and listening!\n')
        print(f'({host}):({port}) Connecting to PLC...\n')
        with LogixDriver('120.123.230.39/0') as plc:
            print(f'({host}):({port}) Connected to PLC!\n')
            while True:
                try:
                    if(kill_threads == True):
                        print(f'({host}):({port}) Thread(s) disrupted, restarting...')
                        break
                    s.listen()
                    conn, addr = s.accept()
                    with conn:
                        print(f"({host}):({port}) Connected by {addr}\n")
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                break
                            plc_result = {}

                            data_txt = data.decode("utf-8")
                        
                            #cleaning message, data_cmd will be 'r' or 'w', data_tag will be '<full_tag_name>'
                            data_list = []
                            data_list = data_txt.split(',')
                            data_list_cmd = data_list[0].split(' ')
                            data_cmd = data_list_cmd[1]
                            data_list_tag = data_list[1].split(' ')
                            data_tag = data_list_tag[2]
                            data_tag = data_tag.strip('}')

                            response_string = '{ok' #beginning of response for either read or write request

                            if(port == 4000):
                                #plc_result = read_plc_dict('1', plc)
                                if(data_cmd == 'r'):
                                    plc_value = read_plc_tag(plc, tag)
                                    response_string = response_string + ', ' + plc_value + '}\n'
                            elif(port == 4001):
                                plc_result = read_plc_dict('2', plc)
                            else:
                                print('Invalid Server Port! Should be : 4000 or 4001')
                            #plc_result_json = json.dumps(plc_result) # result into serialized json
                            #conn.sendall(plc_result_json.encode()) # responds with encoded serialized json string
                            print(response_string)
                            conn.sendall(response_string.encode())
                            #print(f'({host}):({port}) Sent Booleans to {addr}')
                except Exception as e:
                    print(f'({host}):({port}) Exception : {str(e)}')
                    kill_threads = True

def main():
    global kill_threads
    # Thread declaration / initialization
    t1 = threading.Thread(target=start_server, args=["127.0.0.1", 4000])
    t2 = threading.Thread(target=start_server, args=["127.0.0.1", 4001])
    #start_server(HOST, PORT)

    kill_threads = False
    t1.start()
    t2.start()

    t1.join()
    t2.join() # join both threads, useful for try/except restarting and preventing continous 'main()' calls
    pass

#implicit 'main()' declaration
if __name__ == '__main__':
    while(True):
        main()