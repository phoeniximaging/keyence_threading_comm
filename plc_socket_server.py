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
import sys
import time

#HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
#PORT = 4000  # Port to listen on (non-privileged ports are > 1023)

kill_threads = False
change_latch = False

# global variable declarations, some are probably unnecessary(?)

arrayOutTagsSignals = [
    'LoadProgram',
    'StartProgram',
    'EndProgram',
    'EndScan',
    'AbortProgram',
    'Reset'
    ];

arrayOutTags = [
    'LoadProgram',
    'StartProgram',
    'EndProgram',
    'AbortProgram',
    'EndScan',
    'Reset',
    'PartType',
    'PartProgram',
    'ScanNumber',
    'PUN{64}',
    'GMPartNumber{8}',
    'Module',
    'PlantCode',
    'Month',
    'Day',
    'Year',
    'Hour',
    'Minute',
    'Second',
    'QualityCheckOP110',
    'QualityCheckOP120',
    'QualityCheckOP130',
    'QualityCheckOP140',
    'QualityCheckOP150',
    'QualityCheckOP310',
    'QualityCheckOP320',
    'QualityCheckOP330',
    'QualityCheckOP340',
    'QualityCheckOP360',
    'QualityCheckOP370',
    'QualityCheckOP380',
    'QualityCheckOP390',
    'QualityCheckScoutPartTracking'
    #'KeyenceFltCode',
    #'PhoenixFltCode'
    ];


tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(machine_num, plc):
    #print("read_plc_dict, generating list of read tags")
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:HM1450_VS' + machine_num + '.VPC1.O.' + tag;
        #print(newTag);
        readList.append(newTag)
        
    resultsList = plc.read(*readList) # tag, value, type, error
    #print(resultsList)
    readDict = {}

    #print("returned results")
    #print(resultsList)

    for tag in resultsList:
        #key = tag.tag.split(".")[-1]
        key = tag[0] #prints entire tag name, Program:HM1450_VS' + machine_num + '.VPC1.O.' + tag
        #print(key)
        #print(tag)
        readDict[key] = tag[1]

    #print(readDict)
    return readDict
#END read_plc_dict

# read/write functions, have special cases for PUN and GMPartNumber bc they are ARRAYS not single values
def read_plc_tag(plc, single_tag):
    pun_check = 'PUN'
    gm_part_check = 'GMPartNumber'

    if pun_check in single_tag:
        #print(single_tag)
        read_plc = plc.read(single_tag + '{65}')
        #print(read_plc)
        read_plc_value = read_plc[1]
    elif gm_part_check in single_tag:
        #print(single_tag)
        read_plc = plc.read(single_tag + '{9}')
        #print(read_plc)
        read_plc_value = read_plc[1]
    else:
        #print(single_tag)
        read_plc = plc.read(single_tag)
        #print(read_plc)
        read_plc_value = read_plc[1]
    #if((single_tag == 'Program:HM1450_VS14.VPC1.O.LoadProgram') or (single_tag == 'Program:HM1450_VS14.VPC1.O.StartProgram')):
        #print(single_tag)
        #print(read_plc_value)
    return read_plc_value
#END read_plc_tag

def write_plc_tag(plc, single_tag, value):
    pun_check = 'PUN'
    gm_part_check = 'GMPartNumber'

    if pun_check in single_tag:
        plc.write(single_tag + '{65}', value)
    elif gm_part_check in single_tag:
        plc.write(single_tag + '{9}', value)
    else:
        plc.write(single_tag, value)
#END write_plc_tag


def start_server(host, port):
    global kill_threads
    global change_latch

    #initial while True restarts on exception INSIDE thread
    while True:
        kill_threads = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            print(f'({host}):({port}) Alive and listening!\n')
            print(f'({host}):({port}) Connecting to PLC...\n')
            with LogixDriver('120.57.42.114') as plc:
                print(f'({host}):({port}) Connected to PLC!\n')
                loadup_display = {}
                if(port == 4000):
                    loadup_display = read_plc_dict('14', plc)
                elif(port == 4001):
                    loadup_display = read_plc_dict('15', plc)
                print(loadup_display)
                try:
                    while True:
                        if(kill_threads):
                            print(f'({host}):({port}) kill_threads True, restarting threads...')
                            break
                        s.listen() #THIS IS CONSTANTLY LISTENING FOR CONNECTIONS
                        conn, addr = s.accept()
                        with conn:
                            print(f"({host}):({port}) Connected by {addr}\n")
                            while True:
                                data = conn.recv(1024) # reading in data stream
                                if not data:
                                    break # if stream has no data (connection broken most likely), break out of stream
                                request_result = {}
                                data_txt = '' # empty string declaration
                                data_txt = data.decode("utf-8")
                                #print(data_txt)
                                request_result = json.loads(data_txt)
                                #print(request_result)

                                #response_string = '{\"status\": ok, ' #beginning of response for either read or write request
                                #response_string = ''
                                response_dict = {}
                                response_dict_bulk = {}
                                validation_req = False # initial declaration, only validate READING of BOOL tags

                                if(port == 4000):
                                    machine_num = '14'
                                elif(port == 4001):
                                    machine_num = '15'

                                #if(port == 4000):
                                    #plc_result = read_plc_dict('1', plc)

                                if(request_result['cmd'] == 'r'):
                                    #print('READ')
                                    #print()
                                    plc_value = read_plc_tag(plc, request_result['tag']) # single read
                                    '''
                                    validation_req = False
                                    for tag in arrayOutTagsSignals:
                                        if (request_result['tag'] == ('Program:HM1450_VS' + machine_num + '.VPC1.O.' + tag)):
                                            validation_req = True
                                    
                                    if validation_req:
                                        #print(f'({machine_num}) Validating Bool tag...')
                                        plc_value_old = plc_value
                                        valid_count = 0
                                        while(plc_value == plc_value_old):
                                            plc_value = read_plc_tag(plc, request_result['tag']) # single read
                                            valid_count += 1
                                            if(plc_value != plc_value_old):
                                                display_tag = request_result['tag']
                                                print(f'plc_value {display_tag} had a mis-match between reads...')
                                                valid_count = 0 #restart validation reads, must read 5 consecutive SAME values to proceed
                                            
                                            if(valid_count == 5):
                                                print(f'plc_value {display_tag} validated!')
                                                break
                                    '''

                                    ''' bulk read
                                    response_dict_bulk = read_plc_dict(machine_num, plc)
                                    for result in response_dict_bulk:
                                        if(result == request_result['tag']):
                                            response_dict['status'] = "ok"
                                            response_dict['tag'] = result
                                            response_dict['value'] = response_dict_bulk[result]
                                    '''

                                    #print(f'plc_value = {plc_value}')
                                    #response_string = '{"status": "ok", "tag": "' + request_result['tag'] + '", "value": ' + plc_value + '}\n'
                                    response_dict['status'] = "ok"
                                    response_dict['tag'] = request_result['tag']
                                    response_dict['value'] = plc_value

                                elif(request_result['cmd'] == 'w'):
                                    #print('WRITE')
                                    #plc.write(request_result['tag'], request_result['value'])
                                    #print(request_result['tag'])
                                    if '.O.' in request_result['tag']:
                                        print('\n\n***WRITING .O TAG***\n\n')
                                        break
                                    write_plc_tag(plc, request_result['tag'], request_result['value'])
                                    #response_string = response_string + ', ' + data_tag + ', ' + data_tag_value + '}\n'
                                    #response_string = '{"status": "ok"}\n'
                                    response_dict['status'] = "ok"

                                #plc_result_json = json.dumps(plc_result) # result into serialized json
                                #conn.sendall(plc_result_json.encode()) # responds with encoded serialized json string
                                #print(response_string)
                                #print(response_dict)
                                
                                '''
                                if((request_result['tag'] == 'Program:HM1450_VS14.VPC1.I.Heartbeat')
                                    or (request_result['tag'] == 'Program:HM1450_VS14.VPC1.I.Ready')
                                    or (request_result['tag'] == 'Program:HM1450_VS14.VPC1.I.PUN')):
                                    print(request_result['tag'])
                                    print(response_dict)
                                    print(request_result['value'])

                                if(request_result['tag'] == 'Program:HM1450_VS14.VPC1.O.LoadProgram'):
                                    #print(response_dict['value'])
                                    print(response_dict)
                                
                                    if((response_dict['value']) == True and (change_latch == False)):
                                        print('Changed TRUE')
                                        print(request_result['tag'])
                                        print(response_dict['value'])
                                        print(response_dict)
                                        change_latch = True
                                    elif((response_dict['value']) == False and (change_latch == True)):
                                        print('Changed FALSE')
                                        print(request_result['tag'])
                                        print(response_dict['value'])
                                        print(response_dict)
                                        change_latch = False
                                    #print(request_result['value'])
                                if(request_result['tag'] == 'Program:HM1450_VS14.VPC1.O.StartProgram'):
                                    #print(response_dict['value'])
                                    print(response_dict)
                                '''    

                                request_result_json = json.dumps(response_dict)
                                #print(request_result_json)
                                #conn.sendall(response_string.encode())
                                request_result_json = request_result_json + '\n'
                                conn.sendall(request_result_json.encode())
                                #print(f'({port}) Response Sent')
                                #print(f'({host}):({port}) Sent Booleans to {addr}')
                        if(kill_threads):
                            print(f'({host}):({port}) kill_threads True, restarting threads...')
                            break
                except Exception as e:
                    print(f'({host}):({port}) Exception : {str(e)}')
                    kill_threads = True

def main():
    global kill_threads
    global change_latch

    # Thread declaration / initialization
    t1 = threading.Thread(target=start_server, args=["127.0.0.1", 4000])
    t2 = threading.Thread(target=start_server, args=["127.0.0.1", 4001])
    #start_server(HOST, PORT)

    kill_threads = False
    change_latch = False
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    pass

#implicit 'main()' declaration
if __name__ == '__main__':
    while(True):
        main()
        print('Main Loop Disrupted, restarting servers...')