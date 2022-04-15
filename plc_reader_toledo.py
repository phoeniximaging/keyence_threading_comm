from logging import debug
from pycomm3 import LogixDriver

import asyncio
import time
import datetime
#from asyncua import Client, Node, ua
import json
import os
import sys

from random import randrange

from pycomm3.cip.data_types import DINT, UINT
import socket

## Reads PLC dict and prints out as blob, then each field/tag

#global vars
retries = 0
debug_msgs = False
exception_count = 0

ready14_OLD = False
ready15_OLD = False

arrayOutTags = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET',
    'PART_TYPE',
    'PART_PROGRAM',
    'PUN{64}',
    'MODULE',
    #'PLANTCODE',
    'TIMESTAMP_MONTH',
    'TIMESTAMP_DAY',
    'TIMESTAMP_YEAR',
    'TIMESTAMP_HOUR',
    'TIMESTAMP_MINUTE',
    'TIMESTAMP_SECOND'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#order matters!
tagCmds = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET'];

tagDateTime = [
    'TIMESTAMP_MONTH',
    'TIMESTAMP_DAY',
    'TIMESTAMP_YEAR',
    'TIMESTAMP_HOUR',
    'TIMESTAMP_MINUTE',
    'TIMESTAMP_SECOND'];

tagStringInt = [
    'PUN'];

tagInt = [
    'PART_TYPE',
    'PART_PROGRAM'
    ];

tagChar = [
    'MODULE',
    'PLANTCODE'
    ];

def read_plc_dict(plc, machine_num):
    #print("read_plc_dict, generating list of read tags")
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.O.' + tag;
        #print(newTag);
        readList.append(newTag)
        
    resultsList = plc.read(*readList) # tag, value, type, error
    readDict = {}

    #print("returned results")
    #print(resultsList)

    for tag in resultsList:
        key = tag.tag.split(".")[-1]
        #print(key)
        #print(tag)
        readDict[key] = tag

    #print(readDict)
    return readDict

def protected_ord(value):
    if len(value) > 1:
        print("WRONG Below: ")
        print(value)
        value = value[0]
    #print("Returning:")
    #print(value)
    return ord(value)

'''
def opc_write_value(client, idx, machine_num, key, value, datatype):
    opc_from_plc = client.nodes.root.get_child(["0:Objects", 
        f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O." + key])
    opc_from_plc.set_value(value, datatype)
'''

#function to translate PLC int-arrays into ASCII str for OPC
def intArray_to_str(intArray):
    strReturn = ""
    #print(intArray)

    #reads each 'int' from array then appends to 'str' array in char form (per element)
    for i in range(len(intArray)):
        strReturn += chr(intArray[i])

    #print(strReturn)
    return strReturn

#function to translate PLC int-arrays into ASCII str-arrays for OPC
def intArray_to_strArray(intArray):
    #declaring an array of 'str' to hold return value
    strArray = []
    #print(intArray)

    #print()

    #reads each 'int' from array then appends to 'str' array in char form (per element)
    for i in range(len(intArray)):
        strArray.append(chr(intArray[i]))

    #print(strArray)
    return strArray

#end intArray_to_strArray

#function to translate OPC str-arrays into PLC int-arrays
def strArray_to_intArray(strArray):
    #declaring an array of 'int' to hold return value
    intArray = []
    strArray_list = list(strArray)
    #print(strArray_list)
    #print(list(strArray))

    #reads each char from str array then appends to 'intArray' in int form (per element)
    for i in range(len(strArray_list)):
        
        intArray.append(ord(strArray_list[i]))

    return intArray

#end strArray_to_intArray

def TriggerKeyence(server_address_tuple):

    trigger_start_time_total = datetime.datetime.now()

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address =  server_address_tuple #`('localhost', 10000)
    print('connecting to %s port %s' % server_address)
    trigger_start_time = datetime.datetime.now()
    sock.connect(server_address)
    trigger_end_time = datetime.datetime.now()
    time_diff = (trigger_end_time - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    print("Keyence Connected in: " + str(execution_time))

    try:
        # Send data
        message = 'T1\r\n' #'This is the message.  It will be repeated.'
        print('sending "%s"' % message)
        sock.sendall(message.encode())

        data = sock.recv(32)
        print('received "%s"' % data)

        # Look for the response
#        amount_received = 0
#        amount_expected = len(message)
#                                    
#        while amount_received < amount_expected:
#            data = sock.recv(16)
#            amount_received += len(data)
#            print('received "%s"' % data)

    finally:
        print('closing socket')
        sock.close()
        trigger_end_time_total = datetime.datetime.now()
        time_diff = (trigger_end_time_total - trigger_start_time_total)
        execution_time = time_diff.total_seconds() * 1000
        print("Keyence \'TriggerKeyence\' total time: " + str(execution_time))


ready_flag = False

def main():

    #Variable to determine if console output is displayed during run
    global debug_msgs
    global retries
    global ready_flag

    global ready14_OLD
    global ready15_OLD

    print("Alive...")
    time.sleep(5)

    print("Connecting to PLC")
    with LogixDriver("120.123.230.39/0") as plc:
        print()
        print("Initializing! Current Timestamp: " + str(datetime.datetime.now()))
            
        while(True):
            try:

                debug_msgs = False
                rand_value = randrange(75)
                #random.seed(10)
                #print("Random Value:")
                #print(rand_value)
                #print("**************")
                
                #lottery debug msg output
                if (rand_value == 1):
                    #print("\n\n\n\n\n\nIt happened!\n\n\n\n\n\n")
                    debug_msgs = True

                
                if debug_msgs == True:
                    print("Has reconnected: " + str(retries) + ' times')

                start_time_total = datetime.datetime.now()

                #test_results = opc_variables.get_values()
                #print(test_results)
                #print('**************************')

                start_time_total = datetime.datetime.now()

                #logging how long the 'read' takes
                start_time = datetime.datetime.now()
                #populating current tags/values w/ custom read function
                #results_14 = read_plc(plc, '14')
                results_14_dict = read_plc_dict(plc, '1')
                print(results_14_dict)
                print()
                for result in results_14_dict:
                    print(f'{result} : {results_14_dict[result][1]}')
                    print()
                time.sleep(1)
                #print(results_14[0].value)
                end_time = datetime.datetime.now()
                time_diff = (end_time - start_time)
                execution_time = time_diff.total_seconds() * 1000

            except Exception as e:
                #special case for when OPC(?) doesn't respond correctly
                #if str(e) == 'failed to receive reply':
                #    client.close_session
                #    plc.close
                #    #main()

                print("\nexception thrown...")
                print(e)
                print()
                print()
                print("Exception! Current Timestamp: " + str(datetime.datetime.now()))
    
if __name__ == '__main__':
    main()
