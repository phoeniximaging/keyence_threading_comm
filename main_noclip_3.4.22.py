from platform import machine
import threading
import datetime, time
import socket
import csv
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import json
import os
from multiprocessing import Process
import keyboard

'''
This is the first testing thread for Elwema using threading and an all-in-one Python program.

Theoretically runs machine 14 and 15 simultaneously, semi-tested (inconsistent variable delay before/after part being scanned)
'''


# global variable declarations, some are probably unnecessary(?)
arrayOutTags = [
    'LoadProgram',
    'StartProgram',
    'EndProgram',
    'AbortProgram',
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
    'QualityCheckScoutPartTracking',
    'Heartbeat'
    #'KeyenceFltCode',
    #'PhoenixFltCode'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#order matters!
tagCmds = [
    'LoadProgram',
    'EndProgram',
    'StartProgram',
    'AbortProgram',
    'Reset'];

tagDateTime = [
    'Month',
    'Day',
    'Year',
    'Hour',
    'Minute',
    'Second'];

tagStringInt = [
    'PUN',
    'GMPartNumber'];

tagInt = [
    'PartType',
    'PartProgram',
    'ScanNumber',
    #'KeyenceFltCode',
    #'PhoenixFltCode'
    ];

tagChar = [
    'Module',
    'PlantCode',
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
        ];

trigger_count = 0
slow_count = 0
longest_time = 0

current_stage_14 = 0
current_stage_15 = 0

# Keyence socket connections
sock_14 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_14.connect(('172.19.145.80', 8500))
sock_15 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_15.connect(('172.19.146.81', 8500))

lock = threading.Lock()

# Testing
start_timer = datetime.datetime.now()
start_timer_END = datetime.datetime.now()

#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(plc, machine_num):
    #print("read_plc_dict, generating list of read tags")
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:HM1450_VS' + machine_num + '.VPC1.O.' + tag;
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
#END read_plc_dict

#Writing back to PLC to mirror data on LOAD
#TODO: Modify to use running values instead of relying on reads from an OPC server
def write_plc(plc, machine_num, results):

    #logging how long the 'read' takes
    start_time = datetime.datetime.now()

    plc.write(('Program:HM1450_VS' + machine_num + '.VPC1.I.PartType', results['PartType'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PartProgram', results['PartProgram'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.ScanNumber', results['ScanNumber'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PUN{64}', results['PUN'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.GMPartNumber{8}', results['GMPartNumber'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Module', results['Module'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PlantCode', results['PlantCode'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Month', results['Month'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Day', results['Day'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Year', results['Year'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Hour', results['Hour'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Minute', results['Minute'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Second', results['Second'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP110', results['QualityCheckOP110'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP120', results['QualityCheckOP120'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP130', results['QualityCheckOP130'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP140', results['QualityCheckOP140'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP150', results['QualityCheckOP150'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP310', results['QualityCheckOP310'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP320', results['QualityCheckOP320'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP330', results['QualityCheckOP330'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP340', results['QualityCheckOP340'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP360', results['QualityCheckOP360'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP370', results['QualityCheckOP370'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP380', results['QualityCheckOP380'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP390', results['QualityCheckOP390'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckScoutPartTracking', results['QualityCheckScoutPartTracking'][1])
    )

    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    #print('\'plc.write()\' took %d ms to run\n' % (execution_time))
    #print("Finished writing PLC...")
    pass
#END write_plc

def write_plc_flush(plc, machine_num):

    plc_writer_PUN = [72, 101, 108, 108, 111, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35]
    plc_writer_GMPartNumber = [35, 35, 35, 35, 35, 35, 35, 35]

    plc.write(('Program:HM1450_VS' + machine_num + '.VPC1.I.PartType', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PartProgram', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.ScanNumber', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PUN{64}', plc_writer_PUN),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.GMPartNumber{8}', plc_writer_GMPartNumber),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Module', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PlantCode', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Month', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Day', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Year', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Hour', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Minute', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Second', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP110', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP120', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP130', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP140', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP150', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP310', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP320', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP330', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP340', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP360', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP370', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP380', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP390', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckScoutPartTracking', 0)
    )
# end write_plc_flush

#used to verify values when writing back to PLC
def protected_ord(value):
    if len(value) > 1:
        print("WRONG Below: ")
        print(value)
        print()
        value = value[0]
    #print("Returning:")
    #print(value)
    return ord(value)
#END protected_ord

#function to translate PLC int-arrays into ASCII str for OPC
def intArray_to_str(intArray):
    strReturn = ""
    #print(intArray)

    #reads each 'int' from array then appends to 'str' array in char form (per element)
    for i in range(len(intArray)):
        strReturn += chr(intArray[i])

    #print(strReturn)
    return strReturn
#END intArray_to_str

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
#END intArray_to_strArray

#function to translate str-arrays into PLC int-arrays
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
#END strArray_to_intArray

# Triggering Keyence with socket only being connected/closed ONCE (program startup and shutdown)
def TriggerKeyence(sock, item):

    global trigger_count
    global slow_count
    global longest_time
    global start_timer_END

    #verify Keyence(Trg1Ready) is high before we send a 'T1' trigger
    with lock:
        message = 'MR,%Trg1Ready\r\n' #initial read of '%Busy' to ensure scan is actually taking place (%Busy == 1)
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'%Trg1Ready = {data}')

    # looping until '%Busy' == 0
    while(data != b'MR,+0000000001.000000\r'):
        print(f'Keyence(Trg1Ready) was not high, \'T1\' not sent!')
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Trg1Ready\r\n'
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print('TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads

    message = item
    #trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
    with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print('received "%s"\n' % data)
        #start_timer_END = datetime.datetime.now() # END test timer
    #time_diff = (start_timer_END - start_timer)
    #execution_time = time_diff.total_seconds() * 1000
    #print(f'PLC(Start) read to Keyence(T1) read in : {execution_time} ms')

    #am I using these right?(!)
    with lock:
        message = 'MR,%Trg1Ready\r\n' #initial read of '%Busy' to ensure scan is actually taking place (%Busy == 1)
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'%Trg1Ready = {data}')
    #trigger_end_time = datetime.datetime.now() # marking when '%Busy' is read off Keyence
    #time_diff = (trigger_end_time - trigger_start_time)
    #execution_time = time_diff.total_seconds() * 1000
    #print(f'\n\'T1\' sent to \'%Busy\' read in {execution_time} ms\n')
    '''
    if(execution_time > longest_time):
        longest_time = execution_time
    '''
    # looping until '%Busy' == 0
    while(data != b'MR,+0000000000.000000\r'):
    #while(data != b'T1\r'):
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Trg1Ready\r\n'
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print('TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads
    print('Keyence %Trg1Ready verified!')
    
#END 'TriggerKeyence'

#sends specific Keyence Program (branch) info to pre-load/prepare Keyence for Trigger(T1)
def LoadKeyence(sock, item):
    #print('LOADING KEYENCE\n')
    message = item # keyence message
    with lock:
        sock.sendall(message.encode()) # sending branch info
        #print(f'\n\'{item}\' Sent!\n')
        data = sock.recv(32)
        #print('received "%s"\n' % data)

# sends 'TE,0' then 'TE,1' to the Keyence, resetting to original state (ready for new 'T1')
def ExtKeyence(sock):
    #print('ExtKeyence!')
    message = 'TE,0\r\n' # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        data = sock.recv(32)
        #print('\n\'TE,0\' Sent!\n')

        message = 'TE,1\r\n' # setting 'TE,1' to reset
        sock.sendall(message.encode()) # sending, TE,1
        #print('\'TE,1\' Sent!\n')
        data = sock.recv(32)
        #print('received "%s"' % data)
# END 'ExtKeyence'

# reading PLC(EndScan) until it goes high to interrupt current Keyence scan
def monitor_endScan(plc, machine_num, sock):
    print('Listening for PLC(END_SCAN) high\n')
    current = plc.read('Program:HM1450_VS' + machine_num + '.VPC1.O.EndScan')

    while(current[1] != True):
        current = plc.read('Program:HM1450_VS' + machine_num + '.VPC1.O.EndScan')
        #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Heartbeat', True)
        time.sleep(.005)
    print('PLC(END_SCAN) went high!\n')

    ExtKeyence(sock) #function to interrupt Keyence
    pass
#END monitor_endScan

# function to monitor the Keyence tag 'KeyenceNotRunning', when True (+00001.00000) we know Keyence has completed result processing and FTP file write
def monitor_KeyenceNotRunning(sock):
    print('Keyence Processing...')
    #msg = 'MR,#KeyenceNotRunning\r\n'
    msg = 'MR,#KeyenceNotRunning\r\n'
    sock.sendall(msg.encode())
    data = sock.recv(32)
    while(data != b'MR,+0000000001.000000\r'):
        sock.sendall(msg.encode())
        data = sock.recv(32)
        time.sleep(.001)
    print('Keyence Processing Complete!\n')
    pass
#END monitor_KeyenceNotRunning

# primary function, to be used by 14/15 threads
def cycle(machine_num, sock, current_stage):
    global start_timer #testing
    is_paused = False

    print(f'({machine_num}) Connecting to PLC\n')
    with LogixDriver('120.57.42.114') as plc:
        while(True):
            check_pause() # user pause if 'p' is pressed

            #print(f'({machine_num}) Reading PLC\n')
            results_dict = read_plc_dict(plc, machine_num) #initial PLC tag read for 'robot 14' values
            #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Heartbeat', True)
            #print(results_dict['LoadProgram'][1]) #how to print the value of one specific tag

            # PLC read and check to reset system off PLC(Reset) tag
            reset_check = plc.read('Program:HM1450_VS' + machine_num + '.VPC1.O.Reset')
            if (reset_check[1] == True):
                print(f'({machine_num}) Reset Detected! Setting back to Stage 0...')
                current_stage = 0
                print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                write_plc_flush(plc,machine_num)

                plc.write('Program:HM1450_VS' + machine_num + '.VPC1.O.Reset', False)

            #STAGE0 CHECK HERE
            if(current_stage == 0):
                print(f'({machine_num}) Setting Boolean Flags to Stage 0\n')
                plc.write(
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', False),
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', False),
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', False),
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', False)
                )
                #print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                #write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle
                plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', True)
                
                print(f'({machine_num}) Stage 0 : Listening for PLC(LOAD_PROGRAM) = 1\n')
                #reading PLC until LOAD_PROGRAM goes high
                while(results_dict['LoadProgram'][1] != True):
                    check_pause() # user pause if 'p' is pressed
                    results_dict = read_plc_dict(plc, machine_num) # continuous PLC read
                    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Heartbeat', True)
                    #print(csv_results)
                    time.sleep(.005) # 5ms pause between reads

                #print('PLC(LOAD_PROGRAM) went high!\n')
                # Once PLC(LOAD_PROGRAM) goes high, mirror data and set Phoenix(READY) high, signifies end of "loading" process
                plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', False)
                print('Dropping Phoenix(READY) low.\n')

                ''' 
                *Part Program Table (14):*
                1= Cover Face Exhaust Side(625T)
                2= Cover Face Intake Side(625T)
                3= Intake Face(625T)
                4= Front Face(625T)
                5= Cover Face Exhaust Side(675T)
                6= Cover Face Intake Side(675T)
                7= Intake Face(675T)
                8= Front Face(675T)
                9= Cover Face Exhaust Side(45T3)
                10= Cover Face Intake Side(45T3)
                11= Intake Side(45T3)
                12= Front Side(45T3) 
                '''

                keyence_string = '' #building out external Keyence string for scan file naming
                if(machine_num == '14'):
                    if(results_dict['PartProgram'][1] == 1):
                        keyence_string = 'CoverFace-1-625T'
                    elif(results_dict['PartProgram'][1] == 2):
                        keyence_string = 'CoverFace-2-625T'
                    elif(results_dict['PartProgram'][1] == 3):
                        keyence_string = 'IntakeFace-625T'
                    elif(results_dict['PartProgram'][1] == 4):
                        keyence_string = 'FrontFace-625T'
                    elif(results_dict['PartProgram'][1] == 5):
                        keyence_string = 'CoverFace-1-675T'
                    elif(results_dict['PartProgram'][1] == 6):
                        keyence_string = 'CoverFace-2-675T'
                    elif(results_dict['PartProgram'][1] == 7):
                        keyence_string = 'IntakeFace-675T'
                    elif(results_dict['PartProgram'][1] == 8):
                        keyence_string = 'FrontFace-675T'
                    elif(results_dict['PartProgram'][1] == 9):
                        keyence_string = 'CoverFace-1-45T3'
                    elif(results_dict['PartProgram'][1] == 10):
                        keyence_string = 'CoverFace-2-45T3'
                    elif(results_dict['PartProgram'][1] == 11):
                        keyence_string = 'IntakeFace-45T3'
                    elif(results_dict['PartProgram'][1] == 12):
                        keyence_string = 'FrontFace-45T3'
                elif(machine_num == '15'):
                    if(results_dict['PartProgram'][1] == 1):
                        keyence_string = 'DeckFace-1-625T'
                    elif(results_dict['PartProgram'][1] == 2):
                        keyence_string = 'DeckFace-2-625T'
                    elif(results_dict['PartProgram'][1] == 3):
                        keyence_string = 'ExhaustFace-625T'
                    elif(results_dict['PartProgram'][1] == 4):
                        keyence_string = 'RearFace-625T'
                    elif(results_dict['PartProgram'][1] == 5):
                        keyence_string = 'DeckFace-1-675T'
                    elif(results_dict['PartProgram'][1] == 6):
                        keyence_string = 'DeckFace-2-675T'
                    elif(results_dict['PartProgram'][1] == 7):
                        keyence_string = 'ExhaustFace-675T'
                    elif(results_dict['PartProgram'][1] == 8):
                        keyence_string = 'RearFace-675T'
                    elif(results_dict['PartProgram'][1] == 9):
                        keyence_string = 'DeckFace-1-45T3'
                    elif(results_dict['PartProgram'][1] == 10):
                        keyence_string = 'DeckFace-2-45T3'
                    elif(results_dict['PartProgram'][1] == 11):
                        keyence_string = 'ExhaustFace-45T3'
                    elif(results_dict['PartProgram'][1] == 12):
                        keyence_string = 'RearFace-45T3'

                #load_to_trigger_start = datetime.datetime.now()
                #TODO Send branch data to load Keyence for scan
                print(f'Loading: {keyence_string}')
                LoadKeyence(sock,'MW,#PhoenixControlFaceBranch,' + str(results_dict['PartProgram'][1]) + '\r\n') #Keyence loading message, uses PartProgram from PLC to load specific branch
                LoadKeyence(sock,'STW,0,"' + keyence_string + '\r\n') # passing external string to Keyence for file naming (?)
                print(f'({machine_num}) Keyence Loaded!\n')

                #TODO Actually Mirror Data (write back to PLC)
                #print('!Mirroring Data!\n')
                write_plc(plc,machine_num,results_dict) #writing back mirrored values to PLC to confirm LOAD has been processed / sent to Keyence
                #timer_mirrored_to_StartProgram = datetime.datetime.now()
                #LoadProgram_to_Mirrored_diff = (timer_mirrored_to_StartProgram - load_to_trigger_start)
                #execution_time = LoadProgram_to_Mirrored_diff.total_seconds() * 1000
                #print(f'({machine_num}) LoadProgram(high) read until Mirror Complete in {execution_time} ms')

                #csv_results['DATA'] = csv_results_plc['DATA']
                #time.sleep(1) # FINAL SLEEP REMOVAL #artificial pause to see step happening in testing
                print(f'({machine_num}) Data Mirrored, Setting \'READY\' high\n')
                plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', True)
                #time.sleep(3) # FINAL SLEEP REMOVAL
                current_stage += 1 #incrementing out of STAGE0
                print(f'({machine_num}) Stage 1!\nListening for PLC(START_PROGRAM) = 1\n')
            #END STAGE0
            #START STAGE1 : START/END Program
            elif(current_stage == 1):
                #print('Stage 1!\nListening for PLC(START_PROGRAM) = 1')
                #time.sleep(.01) # FINAL SLEEP REMOVAL #10ms artificial delay for testing
                if(results_dict['StartProgram'][1] == True):
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', False)
                    print(f'({machine_num}) PLC(START_PROGRAM) went high! Time to trigger Keyence...\n')

                    start_timer_Trigger_to_Busy = datetime.datetime.now()
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', True) #BUSY BEFORE KEYENCE TRIGGER TEST ***
                    # ARTIFICIAL PAUSE TESTING, DIFFERENT ROBOT / FACE DIFFERENT TIME.SLEEP
                    if(machine_num == '14'):
                        print(f'(14) .5 SECOND ARTIFICIAL DELAY')
                        time.sleep(.5)
                    

                    #Actual Keyence Trigger (T1) here***
                    TriggerKeyence(sock, 'T1\r\n')
                    start_timer_T1_to_EndProgram = datetime.datetime.now()
                    #print('WAITING 2 SECONDS (TEST)')
                    #time.sleep(2) #testing pause***
                    
                    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', True) # Busy goes HIGH while Keyence is scanning
                    #end_timer_Trigger_to_Busy = datetime.datetime.now()
                    diff_timer_Trigger_to_Busy = (start_timer_T1_to_EndProgram - start_timer_Trigger_to_Busy)
                    execution_time = diff_timer_Trigger_to_Busy.total_seconds() * 1000
                    print(f'({machine_num}) PLC(Busy) high to TriggerKeyence in: {execution_time} ms')

                    monitor_endScan(plc, machine_num, sock) # ends Keyence with EndScan
                    end_timer_T1_to_EndScan = datetime.datetime.now()
                    diff_timer_T1_to_EndScan = (end_timer_T1_to_EndScan - start_timer_T1_to_EndProgram)
                    execution_time = diff_timer_T1_to_EndScan.total_seconds() * 1000
                    print(f'({machine_num}) TriggerKeyence to PLC(EndScan) high in: {execution_time} ms')

                    monitor_KeyenceNotRunning(sock) # verify Keyence has processed results and written out FTP files

                    #BUSY HIGH TEST*
                    print(f'({machine_num}) Scan ended! PHOENIX(BUSY) is low\n')
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', False)
                    

                    #TODO PASS/FAIL RESULTS
                    keyenceResults_to_PLC(sock, plc, machine_num)
                    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', True)
                    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', True)
                    #print(f'({machine_num}) PASS/FAIL/DONE data written out\n')
                    #print('PHOENIX(PASS) and PHOENIX(DONE) = 1\n')

                    # Setting Chinmay's Keyence tag high
                    keyence_msg = 'MW,#PhoenixControlContinue,1\r\n'
                    sock.sendall(keyence_msg.encode())
                    print(f'({machine_num}) Sent \'#PhoenixControlContinue,1\' to Keyence!')
                    data = sock.recv(32) #obligatory Keyence read to keep buffer clear

                    print('Stage 1 Complete!\n')
                    current_stage += 1
                    #time.sleep(1) # FINAL SLEEP REMOVAL
                
            #Final Stage, reset to Stage 0 once PLC(END_PROGRAM) and PHOENIX(DONE) have been set low
            elif(current_stage == 2):
                done_check = plc.read('Program:HM1450_VS' + machine_num + '.VPC1.I.Done')
                #print(f'({machine_num}) Stage 2 : Listening to PLC(END_PROGRAM) low to reset back to Stage 0\n')
                if(results_dict['EndProgram'][1] == True):
                    end_timer_T1_to_EndProgram = datetime.datetime.now()
                    diff_timer_T1_to_EndProgram = (end_timer_T1_to_EndProgram - start_timer_T1_to_EndProgram)
                    execution_time = diff_timer_T1_to_EndProgram.total_seconds() * 1000
                    print(f'({machine_num}) TriggerKeyence to PLC(EndProgram) high in: {execution_time} ms')

                    print(f'({machine_num}) PLC(END_PROGRAM) is high. Dropping PHOENIX(DONE) low\n')
                    plc.write(
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', False),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', False),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', False)
                    )
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', False)

                    print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                    write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle

                    print(f'({machine_num}) Artificial Pause (1 seconds)...Then Ready high')
                    time.sleep(1)
                    
                    check_pause() # checking if user wants to pause

                if(results_dict['EndProgram'][1] == False and done_check[1] == False):
                    print(f'({machine_num}) PLC(END_PROGRAM) is low. Resetting PHOENIX to Stage 0\n')
                    
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', True)
                    current_stage = 0 # cycle complete, reset to stage 0
                
                #time.sleep(1) # FINAL SLEEP REMOVAL
            time.sleep(.005) #artificial loop timer
        pass

# function to check if user is holding down 'p' to pause the cycle, then resumes on next 'p'
def check_pause():
    running = True
    display = True
    block = False

    #print('Checking for \'p\' to pause...')

    while (running == True):
        if keyboard.is_pressed('p'):
            if block == False:
                display = not display
                block = True
        else:
            block = False
            running = False
        if display:
            #print('No Pause')
            #time.sleep(1)
            pass
        else:
            print('Pausing!')
            time.sleep(5) #stops accidental toggle
            while(running == True):
                print('Paused...')
                if keyboard.is_pressed('p'):
                    running = False
                    print('Unpause!')
                    time.sleep(5) #stops accidental toggle
                time.sleep(1)
#END check_pause

def heartbeat(machine_num):
    with LogixDriver('120.57.42.114') as plc:
        print(f'({machine_num}) Heartbeat thread connected to PLC. Writing \'Heartbeat\' high every 1 second')
        while(True):
            plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Heartbeat', True)
            #print(f'({machine_num}) Heartbeat written HIGH')
            time.sleep(1)
#END heartbeat

def keyenceResults_to_PLC(sock, plc, machine_num):
    #TODO read results from Keyence then pass to proper tags on PLC
    result_messages = ['MR,#ReportDefectCount\r\n', 'MR,#ReportLargestDefectSize\r\n', 'MR,#ReportLargestDefectZoneNumber\r\n']
    results = []

    # sending result messages to Keyence, then cleaning results to 'human-readable' list
    for msg in result_messages:
        sock.sendall(msg.encode())
        data = sock.recv(32)
        keyence_value_raw = str(data).split('.')
        keyence_value_raw = keyence_value_raw[0].split('+')
        keyence_value = int(keyence_value_raw[1])
        results.append(keyence_value)

    # writing normalized Keyence results to proper PLC tags
    plc.write(
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Defect_Number', results[0]),
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Defect_Size', results[1]),
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectZone', results[2]),
    )
    print('Keyence Results written to PLC!')

#END keyenceResults_to_PLC

#START main()
def main():
    global current_stage_14 #keeps track of which stage program is currently in from the timing process
    global current_stage_15

    #declaring threads, does not run
    #t1 = threading.Thread(target=TriggerKeyence, args=[sock, 'T1\r\n']) #thread1, passing in socket connection and 'T1' keyence command
    #t2 = threading.Thread(target=ExtKeyence, args=[sock, 'TE,0\r\n', 'TE,1\r\n']) #thread2, uses 'TE,0' and 'TE,1' to cancel while scanning and reset to original state

    # original threading tests
    
    t1 = threading.Thread(target=cycle, args=['14', sock_14, current_stage_14])
    t2 = threading.Thread(target=cycle, args=['15', sock_15, current_stage_15])

    t1_heartbeat = threading.Thread(target=heartbeat, args=['14'])
    t2_heartbeat = threading.Thread(target=heartbeat, args=['15'])

    print("Starting Threads (14 & 15)...")
    t1.start()
    t2.start()
    #t1.join()
    #t2.join() # making sure threads complete before moving forward

    print("Starting Heartbeat Threads (14 & 15)")
    t1_heartbeat.start()
    t2_heartbeat.start()
    

    '''
    p1 = Process(target=cycle, args=('14', sock_14, current_stage_14))
    p1.start()
    p2 = Process(target=cycle, args=('15', sock_15, current_stage_15))
    p2.start()
    p1.join()
    p2.join()
    '''

    #print('This code is beyond the threads!')

#END 'main'

#implicit 'main()' declaration
if __name__ == '__main__':
    main()
    '''
    for x in range(1000):
        print(f'Main Loop {x}')
        main()
        #time.sleep(3) # time between cycles to eyeball if multiple scans are actually taking place
    '''