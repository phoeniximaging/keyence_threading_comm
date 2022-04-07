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
import keyboard

'''
First iteration of error handling for Grob system with automated cycling.

Uses 'kill_threads' global boolean to kill and restart all threads if any exceptions are thrown

Sends PhoenixFltCodes to PLC
'''

trigger_count = 0
slow_count = 0
longest_time = 0

current_stage_1 = 0
current_stage_2 = 0

# KEYENCE socket connections
#sock_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock_1.connect(('172.19.147.82', 8500)) # GROB address, Keyence head #1

#sock_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock_2.connect(('172.19.148.83', 8500)) # GROB address, Keyence head #2

#lock = threading.Lock()

kill_threads = False # global boolean to stop all threads on exception

arrayOutTags = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET',
    'PART_TYPE',
    'PART_PROGRAM',
    #'SCAN_NUMBER',
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
    'PART_PROGRAM',
    'SCAN_NUMBER'
    ];

tagChar = [
    'MODULE',
    'PLANTCODE'
    ];

def read_plc_dict(plc, machine_num):
    #print("read_plc_dict, generating list of read tags")
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.' + tag;
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

#Writing back to PLC to mirror data on LOAD
#TODO: Modify to use running values instead of relying on reads from an OPC server
def write_plc(plc, machine_num, results):
    #logging how long the 'read' takes
    start_time = datetime.datetime.now()

    plc.write(('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PART_TYPE', results['PART_TYPE'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PART_PROGRAM', results['PART_PROGRAM'][1]),
    #('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.SCAN_NUMBER', results['SCAN_NUMBER'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PUN{64}', results['PUN'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.MODULE', results['MODULE'][1]),
    #('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PLANTCODE', results['PLANTCODE'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MONTH', results['TIMESTAMP_MONTH'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_DAY', results['TIMESTAMP_DAY'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_YEAR', results['TIMESTAMP_YEAR'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_HOUR', results['TIMESTAMP_HOUR'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MINUTE', results['TIMESTAMP_MINUTE'][1]),
    ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_SECOND', results['TIMESTAMP_SECOND'][1])
    )

    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print('\'plc.write()\' took %d ms to run' % (execution_time))
    #print("Finished writing PLC...")
    pass
#END write_plc

# Flushes PLC data mirroring tags (to 0)
def write_plc_flush(plc, machine_num):

    plc_writer_PUN = [72, 101, 108, 108, 111, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35]

    plc.write(
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PART_TYPE', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PART_PROGRAM', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PUN{64}', plc_writer_PUN),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.MODULE', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MONTH', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_DAY', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_YEAR', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_HOUR', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MINUTE', 0),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_SECOND', 0)
    )
# end write_plc_flush

# Triggering Keyence with socket only being connected/closed ONCE (program startup and shutdown)
def TriggerKeyence(sock, machine_num, item):

    global trigger_count
    global slow_count
    global longest_time
    global start_timer_END

    #verify Keyence(Trg1Ready) is high before we send a 'T1' trigger
    #with lock:
    message = 'MR,%Trg1Ready\r\n' #initial read of '%BUSY' to ensure scan is actually taking place (%BUSY == 1)
    sock.sendall(message.encode())
    data = sock.recv(32)
    print(f'({machine_num}) %Trg1Ready = {data}')

    # looping until '%BUSY' == 0
    while(data != b'MR,+0000000001.000000\r'):
        print(f'Keyence(Trg1Ready) was not high, \'T1\' not sent!')
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Trg1Ready\r\n'
        #with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'({machine_num}) TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads

    message = item
    trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
    #with lock:
    sock.sendall(message.encode())
    data = sock.recv(32)
    print(f'({machine_num}) received "%s"\n' % data)
        #start_timer_END = datetime.datetime.now() # END test timer
    #time_diff = (start_timer_END - start_timer)
    #execution_time = time_diff.total_seconds() * 1000
    #print(f'PLC(Start) read to Keyence(T1) read in : {execution_time} ms')

    #am I using these right?(!)
    #with lock:
    message = 'MR,%Trg1Ready\r\n' #initial read of '%BUSY' to ensure scan is actually taking place (%BUSY == 1)
    sock.sendall(message.encode())
    data = sock.recv(32)
    print(f'%Trg1Ready = {data}')
    
    '''
    if(execution_time > longest_time):
        longest_time = execution_time
    '''
    # looping until '%BUSY' == 0
    while(data != b'MR,+0000000000.000000\r'):
    #while(data != b'T1\r'):
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Trg1Ready\r\n'
        #with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'({machine_num})TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads
    #print('Keyence %Trg1Ready verified!')
    trigger_end_time = datetime.datetime.now() # marking when '%BUSY' is read off Keyence
    time_diff = (trigger_end_time - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    print(f'\n({machine_num}) \'T1\' sent to \'%Trg1Ready\' verified in {execution_time} ms\n')
#END 'TriggerKeyence'

#sends specific Keyence Program (branch) info to pre-load/prepare Keyence for Trigger(T1)
def LoadKeyence(sock, item, machine_num):
    #print(f'\n({machine_num}) LoadKeyence Started : {item} \n')
    
    message = 'MR,%Busy\r\n' #initial read of '%BUSY' to ensure scan is actually taking place (%BUSY == 1)
    sock.sendall(message.encode())
    data = sock.recv(32)
    #print(f'%Busy = {data}\n')
    # looping until '%BUSY' == 0, won't load Keyence with info until it's confirmed NOT busy
    while(data != b'MR,+0000000000.000000\r'):
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Busy\r\n'
        #with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print('Pulling Keyence(Busy) for low...')
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads
    
    #message = 'MR\r\n' #initial read of '%BUSY' to ensure scan is actually taking place (%BUSY == 1)
    #sock.sendall(message.encode())
    #data = sock.recv(32) #clearing out Keyence dirty messages?
    #print(f'({machine_num}) LOADING KEYENCE {item} \n')
    message = item # setting 'TE,0' first
    #print(f'({machine_num}) {message} \n')
    #with lock:
    sock.sendall(message.encode()) # sending TE,0
    #print(f'\n({machine_num}) \'{item}\' Sent!')
    data = sock.recv(32)
    #print(f'\n({machine_num}) received "%s"' % data)

# sends 'TE,0' then 'TE,1' to the Keyence, resetting to original state (ready for new 'T1')
def ExtKeyence(sock):
    #print('ExtKeyence!')
    message = 'TE,0\r\n' # setting 'TE,0' first
    #with lock:
    sock.sendall(message.encode()) # sending TE,0
    data = sock.recv(32)
    #print('\n\'TE,0\' Sent!\n')

    message = 'TE,1\r\n' # setting 'TE,1' to reset
    sock.sendall(message.encode()) # sending, TE,1
    #print('\'TE,1\' Sent!\n')
    data = sock.recv(32)
    #print('received "%s"' % data)
# END 'ExtKeyence'

### THE PASTE

# reading PLC(END_SCAN) until it goes high to interrupt current Keyence scan
def monitor_END_SCAN(plc, machine_num, sock):
    print(f'({machine_num}) Listening for PLC(END_SCAN) high\n')
    current = plc.read(
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.END_SCAN'),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET')
    )

    # checking END_SCAN and RESET
    while((current[0][1] == False) and (current[1][1] == False)):
        current = plc.read(
            ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.END_SCAN'),
            ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET')
        )
        #print(f'{machine_num} END_SCAN : {current[0][1]} | RESET : {current[1][1]}')
        time.sleep(.005)
    print(f'({machine_num}) PLC(END_SCAN) went high!\n')

    ExtKeyence(sock) #function to interrupt Keyence
    pass
#END monitor_END_SCAN

# function to monitor the Keyence tag 'KeyenceNotRunning', when True (+00001.00000) we know Keyence has completed result processing and FTP file write
def monitor_KeyenceNotRunning(sock, machine_num):
    #print(f'({machine_num}) Keyence Processing...')
    #msg = 'MR,#KeyenceNotRunning\r\n'
    msg = 'MR,#KeyenceNotRunning\r\n'
    sock.sendall(msg.encode())
    data = sock.recv(32)
    while(data != b'MR,+0000000001.000000\r'):
        sock.sendall(msg.encode())
        data = sock.recv(32)
        time.sleep(.001)
    #print(f'({machine_num}) Keyence Processing Complete!\n')
    pass
#END monitor_KeyenceNotRunning

# primary function, to be used by 14/15 threads
def cycle(machine_num, current_stage):
    global start_timer #testing
    program_swapped = False # latch for switching from ring seal to other Keyence program
    is_paused = False
    global kill_threads

    part_result = '' # string to hold result info per part, then log into a .txt once complete

    print(f'({machine_num}) Connecting to PLC...\n')
    with LogixDriver('120.123.230.39/0') as plc:
        print(f'({machine_num}) Connected to PLC')
        try:
            # Keyence socket connections
            if(machine_num == '1'):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('172.19.145.80', 8500))
            elif(machine_num == '2'):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('172.19.146.81', 8500))
            while(True):
                if(kill_threads):
                    print(f'({machine_num}) kill_threads detected! Restarting threads...')
                    break
                #check_pause() # user pause if 'p' is pressed

                #print(f'({machine_num}) Reading PLC\n')
                results_dict = read_plc_dict(plc, machine_num) #initial PLC tag read for 'robot 14' values
                #print(results_dict['LOAD_PROGRAM'][1]) #how to print the value of one specific tag

                # PLC read and check to RESET system off PLC(RESET) tag
                RESET_check = plc.read('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET')
                if (RESET_check[1] == True):
                    RESET_check = plc.read('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET')
                    print(f'({machine_num}) (Pre-Load) RESET Detected! Setting back to Stage 0...')
                    current_stage = 0
                    print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                    write_plc_flush(plc,machine_num)
                    #plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET_ACK', True)
                    plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', True)

                    while(RESET_check[1] != False):
                        print(f'({machine_num}) (Pre-Load) Waiting on PLC(RESET) low...')
                        RESET_check = plc.read('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET')
                        time.sleep(.005)

                    #print(f'({machine_num}) Reset Complete! Phoenix(READY) going high')
                    #plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', True)

                #STAGE0 CHECK HERE
                if(current_stage == 0):
                    print(f'({machine_num}) Setting Boolean Flags to Stage 0\n')
                    
                    plc.write(
                        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.BUSY', False),
                        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.DONE', False),
                        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PASS', False),
                        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.FAIL', False)
                    )
                    #print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                    #write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle
                    plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', True)

                    print(f'({machine_num}) Flushing PLC data (Stage 0)')
                    write_plc_flush(plc,machine_num)
                    
                    print(f'({machine_num}) Stage 0 : Listening for PLC(LOAD_PROGRAM) = 1\n')
                    #reading PLC until LOAD_PROGRAM goes high
                    while(results_dict['LOAD_PROGRAM'][1] != True):
                        #check_pause() # user pause if 'p' is pressed
                        results_dict = read_plc_dict(plc, machine_num) # continuous PLC read
                        if (results_dict['RESET'][1] == True):
                            RESET_check = plc.read('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET')
                            print(f'({machine_num}) (During Load) RESET Detected! Setting back to Stage 0...')
                            current_stage = 0
                            print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                            write_plc_flush(plc,machine_num)
                            #plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET_ACK', True)
                            plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', True)
                            print(f'({machine_num}) (Loading) Waiting on PLC(RESET) low...')

                            while(RESET_check[1] != False):
                                RESET_check = plc.read('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.O.RESET')
                                time.sleep(.005)

                            #print(f'({machine_num}) Reset Complete! Phoenix(READY) going high')
                            #plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', True)
                            
                        #print(csv_results)
                        time.sleep(.005) # 5ms pause between reads

                    #print('PLC(LOAD_PROGRAM) went high!\n')
                    # Once PLC(LOAD_PROGRAM) goes high, mirror data and set Phoenix(READY) high, signifies end of "loading" process
                    plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', False)
                    print(f'({machine_num}) Dropping Phoenix(READY) low.\n')

                    ''' PART_PROGRAM mapping
                    1=Deck Face Scan 1, 
                    2=Deck Face Scan 2, 
                    3=Deck Face Scan 3, 
                    4=Rear Face Scan 1, 
                    5=Rear Face Scan 2, 
                    6=Rear Face Scan 3, 
                    7=Front Face Scan 1,
                    8=Front Face Scan 2, 
                    9=Front Face Scan 3, 
                    10=Pan Rail Face 1, 
                    11=Pan Rail Face 2, 
                    12=Pan Rail Face 3, 
                    41=Cylinder Bore 1, 
                    42=Cylinder Bore 2, 
                    43=Cylinder Bore 3, 
                    44=Cylinder Bore 4
                    *Note Scan 1 - 12 are acquired on XG-X2902LJ Controller, Scan 41 - 44 are acquired on XG-X2502 Controller
                    '''

                    keyence_string = '' #building out external Keyence string for scan file naming
                    if(machine_num == '1'):
                        if(results_dict['PART_PROGRAM'][1] == 1):
                            keyence_string = 'Deck_Face_1'
                            #KeyenceSwapCheck(sock,machine_num,'1') # ensures Keyence has the correct program loaded
                        elif(results_dict['PART_PROGRAM'][1] == 2):
                            keyence_string = 'Deck_Face_2'
                        elif(results_dict['PART_PROGRAM'][1] == 3):
                            keyence_string = 'Deck_Face_3'
                        elif(results_dict['PART_PROGRAM'][1] == 4):
                            keyence_string = 'Rear_Face_1'
                        elif(results_dict['PART_PROGRAM'][1] == 5):
                            keyence_string = 'Rear_Face_2'
                        elif(results_dict['PART_PROGRAM'][1] == 6):
                            keyence_string = 'Rear_Face_3'
                        elif(results_dict['PART_PROGRAM'][1] == 7):
                            keyence_string = 'Front_Face_1'
                        elif(results_dict['PART_PROGRAM'][1] == 8):
                            keyence_string = 'Front_Face_2'
                        elif(results_dict['PART_PROGRAM'][1] == 9):
                            keyence_string = 'Front_Face_3'
                        elif(results_dict['PART_PROGRAM'][1] == 10):
                            keyence_string = 'Pan_Rail_1'
                        elif(results_dict['PART_PROGRAM'][1] == 11):
                            keyence_string = 'Pan_Rail_2'
                        elif(results_dict['PART_PROGRAM'][1] == 12):
                            keyence_string = 'Pan_Rail_3'
                    elif(machine_num == '2'):
                        if(results_dict['PART_PROGRAM'][1] == 41):
                            #keyence_string = 'Case_Rear_Extension_1_Sealing_Face_Section_1'
                            keyence_string = 'Cylinder_Bore_1'
                        elif(results_dict['PART_PROGRAM'][1] == 42):
                            #keyence_string = 'Case_Rear_Extension_1_Sealing_Face_Section_2'
                            keyence_string = 'Cylinder_Bore_2'
                        elif(results_dict['PART_PROGRAM'][1] == 43):
                            keyence_string = 'Cylinder_Bore_3'
                        elif(results_dict['PART_PROGRAM'][1] == 44):
                            keyence_string = 'Cylinder_Bore_4'

                    pun_str = intArray_to_str(results_dict['PUN'][1])

                    #load_to_trigger_start = datetime.datetime.now()
                    #TODO Send branch data to load Keyence for scan
                    print(f'({machine_num}) Loading: {keyence_string}')
                    LoadKeyence(sock,'MW,#PhoenixControlFaceBranch,' + str(results_dict['PART_PROGRAM'][1]) + '\r\n', machine_num) #Keyence loading message, uses PART_PROGRAM from PLC to load specific branch
                    LoadKeyence(sock,'STW,0,"' + pun_str + '_' + keyence_string + '\r\n', machine_num) # PASSing external string to Keyence for file naming (?)
                    #LoadKeyence(sock,'STW,0,"' + keyence_string + '\r\n', machine_num) # PASSing external string to Keyence for file naming (?)
                    LoadKeyence(sock,'OW,42,"' + keyence_string + '-ResultOutput.csv\r\n', machine_num) # .csv file naming loads
                    LoadKeyence(sock,'OW,43,"' + keyence_string + '-10Largest.csv\r\n', machine_num)
                    LoadKeyence(sock,'OW,44,"' + keyence_string + '-10Locations.csv\r\n', machine_num)
                    print(f'({machine_num}) Keyence Loaded!\n')

                    #PUN_display = results_dict['PUN'] # because I don't know how to print this with apostrophes around dict keys :D
                    # Printing PUN per Grob's request
                    #print(f'***\n({machine_num}) PUN : {PUN_display}***\n')

                    #TODO Actually Mirror Data (write back to PLC)
                    #print('!Mirroring Data!\n')
                    write_plc(plc,machine_num,results_dict) #writing back mirrored values to PLC to confirm LOAD has been processed / sent to Keyence
                    #timer_mirrored_to_START_PROGRAM = datetime.datetime.now()
                    #LOAD_PROGRAM_to_Mirrored_diff = (timer_mirrored_to_START_PROGRAM - load_to_trigger_start)
                    #execution_time = LOAD_PROGRAM_to_Mirrored_diff.total_seconds() * 1000
                    #print(f'({machine_num}) LOAD_PROGRAM(high) read until Mirror Complete in {execution_time} ms')

                    #csv_results['DATA'] = csv_results_plc['DATA']
                    #time.sleep(1) # FINAL SLEEP REMOVAL #artificial pause to see step happening in testing
                    print(f'({machine_num}) Data Mirrored, Setting \'READY\' high\n')
                    plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', True)
                    #time.sleep(3) # FINAL SLEEP REMOVAL
                    current_stage += 1 #incrementing out of STAGE0
                    print(f'({machine_num}) Stage 1!\nListening for PLC(START_PROGRAM) = 1\n')
                #END STAGE0
                #START STAGE1 : START/END Program
                elif(current_stage == 1):
                    #print('Stage 1!\nListening for PLC(START_PROGRAM) = 1')

                    #if(start_check[1] == True):
                    if(results_dict['START_PROGRAM'][1] == True):
                        plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', False)
                        print(f'({machine_num}) PLC(START_PROGRAM) went high! Time to trigger Keyence...\n')
                        
                        #Actual Keyence Trigger (T1) here***
                        TriggerKeyence(sock, machine_num, 'T1\r\n')
                        start_timer_T1_to_END_PROGRAM = datetime.datetime.now()
                        #print('WAITING 2 SECONDS (TEST)')
                        #time.sleep(2) #testing pause***

                        start_timer_Trigger_to_BUSY = datetime.datetime.now()
                        plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.BUSY', True) #BUSY BEFORE KEYENCE TRIGGER TEST ***
                        end_timer_BUSYWrite = datetime.datetime.now()
                        time_diff_BUSYWrite = (end_timer_BUSYWrite - start_timer_Trigger_to_BUSY)
                        execution_time = time_diff_BUSYWrite.total_seconds() * 1000
                        print(f'({machine_num}) Writing \'BUSY\' to PLC took: {execution_time} ms')
                        
                        #plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.BUSY', True) # BUSY goes HIGH while Keyence is scanning
                        #end_timer_Trigger_to_BUSY = datetime.datetime.now()
                        diff_timer_Trigger_to_BUSY = (start_timer_T1_to_END_PROGRAM - start_timer_Trigger_to_BUSY)
                        execution_time = diff_timer_Trigger_to_BUSY.total_seconds() * 1000
                        print(f'({machine_num}) PLC(BUSY) high to TriggerKeyence in: {execution_time} ms')

                        #if(results_dict['PART_PROGRAM'][1] != 1):
                            #print(f'({machine_num}) PART_PROGRAM : ' + str(results_dict['PART_PROGRAM'][1]))

                        monitor_END_SCAN(plc, machine_num, sock) # ends Keyence with END_SCAN

                        end_timer_T1_to_END_SCAN = datetime.datetime.now()
                        diff_timer_T1_to_END_SCAN = (end_timer_T1_to_END_SCAN - start_timer_T1_to_END_PROGRAM)
                        execution_time = diff_timer_T1_to_END_SCAN.total_seconds() * 1000
                        print(f'({machine_num}) TriggerKeyence to PLC(END_SCAN) high in: {execution_time} ms')

                        monitor_KeyenceNotRunning(sock, machine_num) # verify Keyence has processed results and written out FTP files

                        #BUSY HIGH TEST*
                        print(f'({machine_num}) Scan ended! PHOENIX(BUSY) is low\n')
                        plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.BUSY', False)

                        #TODO PASS/FAIL RESULTS
                        keyence_results = keyenceResults_to_PLC(sock, plc, machine_num, keyence_string) # sends Keyence result data to the PLC while simultaneously populating a local result list to write out into a .txt file
                        create_csv(machine_num, results_dict, keyence_results, keyence_string) # creating result .csv (.txt) file

                        #check if we're ready to write out a parts results
                        part_result = write_part_results(machine_num, part_result, results_dict, keyence_results) #appends to result string, writes out file and clears string if on final scan of part

                        # Setting Chinmay's Keyence tag high
                        keyence_msg = 'MW,#PhoenixControlContinue,1\r\n'
                        sock.sendall(keyence_msg.encode())
                        print(f'({machine_num}) Sent \'#PhoenixControlContinue,1\' to Keyence!')
                        data = sock.recv(32) #obligatory Keyence read to keep buffer clear

                        print(f'({machine_num}) Stage 1 Complete!\n')
                        current_stage += 1
                        #time.sleep(1) # FINAL SLEEP REMOVAL
                    
                #Final Stage, RESET to Stage 0 once PLC(END_PROGRAM) and PHOENIX(DONE) have been set low
                elif(current_stage == 2):
                    DONE_check = plc.read('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.DONE')
                    #print(f'({machine_num}) Stage 2 : Listening to PLC(END_PROGRAM) low to RESET back to Stage 0\n')
                    if(results_dict['END_PROGRAM'][1] == True):
                        end_timer_T1_to_END_PROGRAM = datetime.datetime.now()
                        diff_timer_T1_to_END_PROGRAM = (end_timer_T1_to_END_PROGRAM - start_timer_T1_to_END_PROGRAM)
                        execution_time = diff_timer_T1_to_END_PROGRAM.total_seconds() * 1000
                        #print(f'({machine_num}) TriggerKeyence to PLC(END_PROGRAM) high in: {execution_time} ms')

                        print(f'({machine_num}) PLC(END_PROGRAM) is high. Dropping PHOENIX(DONE) low\n')
                        plc.write(
                            ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.BUSY', False),
                            ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PASS', False),
                            ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.FAIL', False)
                        )
                        plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.DONE', False)

                        print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                        write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle

                        print(f'({machine_num}) Artificial Pause (1 seconds)...Then READY high')
                        time.sleep(1)
                        
                        #check_pause() # checking if user wants to pause

                    if(results_dict['END_PROGRAM'][1] == False and DONE_check[1] == False):
                        print(f'({machine_num}) PLC(END_PROGRAM) is low. Reseting PHOENIX to Stage 0\n')
                        
                        plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.READY', True)
                        current_stage = 0 # cycle complete, RESET to stage 0
                    
                    #time.sleep(1) # FINAL SLEEP REMOVAL
                if(kill_threads == True):
                    print(f'({machine_num}) Cycle : kill_threads high, restarting all threads')
                    break # Kill thread if global is set True for any reason
                time.sleep(.005) #artificial loop timer
        except Exception as e:
            if(str(e) == '[WinError 10054] An existing connection was forcibly closed by the remote host'):
                print(f'({machine_num}) Keyence Connection Error, sending PhoenixFltCode : 1')
                plc.write(
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 1),
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', True)
                )
            if(str(e) == 'failed to receive reply'):
                print(f'({machine_num}) Keyence Connection Error, sending PhoenixFltCode : 4')
                plc.write(
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 4),
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', True)
                )
            print(f'({machine_num}) Exception! {e}')
            kill_threads = True # global to stop/restart all threads

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
#END #check_pause

# pulses heartbeat tag every second, on independent thread(s) per machine
def heartbeat(machine_num):
    with LogixDriver('120.123.230.39/0') as plc:
        print(f'({machine_num}) Heartbeat thread connected to PLC. Writing \'HEARTBEAT\' high every 1 second')
        while(True):
            plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.HEARTBEAT', True)
            #print(f'({machine_num}) Heartbeat written HIGH')
            time.sleep(1)
            if(kill_threads == True):
                print(f'({machine_num}) Heartbeat : kill_threads high, restarting all threads')
                break # Kill thread if global is set True for any reason
#END heartbeat

# read defect information from the Keyence, then PASSes that as well as PASS,FAIL,DONE to PLC
def keyenceResults_to_PLC(sock, plc, machine_num, face_name):
    #TODO read results from Keyence then PASS to proper tags on PLC
    result_messages = [
        #'MR,#ReportDefectCount\r\n',
        #'MR,#ReportLargestDefectSize\r\n',
        #'MR,#ReportLargestDefectZoneNumber\r\n',
        'MR,#ReportPass\r\n',
        'MR,#ReportFail\r\n'
        ]
    results = []

    # sending result messages to Keyence, then cleaning results to 'human-readable' list
    for msg in result_messages:
        sock.sendall(msg.encode())
        data = sock.recv(32)
        keyence_value_raw = str(data).split('.')
        keyence_value_raw = keyence_value_raw[0].split('+')
        keyence_value = int(keyence_value_raw[1])
        results.append(keyence_value)

    print(f'({machine_num}) {face_name} Keyence Results : {results}')
    #print(f'({machine_num}) WRITING ABOVE VALUES TO PLC IN 10 SECONDS!...')
    #time.sleep(10)

    # writing normalized Keyence results to proper PLC tags
    plc.write(
        #('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.DEFECT_NUMBER', results[0]),
        #('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.DEFECT_SIZE', results[1]),
        #('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.DEFECT_ZONE', results[2]),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.PASS', results[0]),
        ('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.FAIL', results[1]),
    )
    #print(f'({machine_num}) PASS = {results[3]} ; FAIL = {results[4]}')
    plc.write('Program:BM650CA01.PorosityInspect.CAM0' + machine_num + '.I.DONE', True)
    print(f'({machine_num}) Keyence Results written to PLC!')

    return results

#END keyenceResults_to_PLC

# used to ensure the correct Keyence program is loaded for the part being processed (only applicable for machine#1 @ Grob)
def KeyenceSwapCheck(sock,machine_num,program_num):
    print(f'({machine_num}) Validating Keyence has proper program loaded...\n')
    msg = 'PR\r\n'

    #with lock:
    sock.sendall(msg.encode())
    data = sock.recv(32)
    #print('received "%s"' % data)

    keyence_value_raw = str(data).split(',')
    keyence_value_raw = str(keyence_value_raw[2]).split('\\')
    print(f'({machine_num}) Keyence currently has program : {keyence_value_raw[0][3]} loaded')
    keyence_value = keyence_value_raw[0][3] # current program number loaded on Keyence
    
    if(keyence_value != program_num):
        print(f'({machine_num}) Swapping Keyence program to: {program_num}')
        LoadKeyence(sock,'PW,1,' + program_num + '\r\n', machine_num) # ring seal is specific program
    pass
#END KeyenceSwapCheck

# George's request for a .csv file per inspection
def create_csv(machine_num, results, keyence_results, face_name):
    #E:\FTP\172.19.146.81\xg\result
    file_name = '' #empty string for .csv file name
    if(machine_num == '1'):
        file_name = 'E:\\FTP\\172.19.147.82\\xg\\result'
    elif(machine_num == '2'):
        file_name = 'E:\\FTP\\172.19.148.83\\xg\\result'
    file_name = file_name + '\\' + face_name + '.txt'
    with open(file_name, 'w', newline='') as f:
        f.write('PART_TYPE_2, ' + str(results['PART_TYPE'][1]) + '\n')
        f.write('PART_PROGRAM_2, ' + str(results['PART_PROGRAM'][1]) + '\n')
        f.write('PUN_2, ' + intArray_to_str(results['PUN'][1]) + '\n')
        f.write('MODULE_2, ' + str(results['MODULE'][1]) + '\n')
        f.write('MONTH_2, ' + str(results['TIMESTAMP_MONTH'][1]) + '\n')
        f.write('DAY_2, ' + str(results['TIMESTAMP_DAY'][1]) + '\n')
        f.write('YEAR_2, ' + str(results['TIMESTAMP_YEAR'][1]) + '\n')
        f.write('HOUR_2, ' + str(results['TIMESTAMP_HOUR'][1]) + '\n')
        f.write('MINUTE_2, ' + str(results['TIMESTAMP_MINUTE'][1]) + '\n')
        f.write('SECOND_2, ' + str(results['TIMESTAMP_SECOND'][1]) + '\n')
        f.write('PASS_2, ' + str(keyence_results[0]) + '\n')
        f.write('FAIL_2, ' + str(keyence_results[1]) + '\n')

    pass
#END create_csv

# Gerry's request to log all results per part in one continuous file
def write_part_results(machine_num, part_result, results_dict, keyence_results):
    if(machine_num == '1'):
        if(results_dict['PART_PROGRAM'][1] == 4):
            part_result = part_result + str(keyence_results[0]) # final append to string before writing out to .txt file
            file_name = '' #empty string for .txt file name
            file_name = 'E:\\part_results_consolidated\\machine_2.txt'
            with open(file_name, 'a', newline='') as f:
                f.write(str(datetime.datetime.now()) + '\n')
                f.write(part_result + '\n\n')
                part_result = ''
                return part_result # clearing then returning pass result for next part
        else:
            part_result = part_result + str(keyence_results[0]) + ', ' # appending pass/fail data to part_result string if we're not @ end of the part
            return part_result
    elif(machine_num == '2'):
        if(results_dict['PART_PROGRAM'][1] == 10):
            part_result = part_result + str(keyence_results[0]) # final append to string before writing out to .txt file
            file_name = '' #empty string for .txt file name
            file_name = 'E:\\part_results_consolidated\\machine_3.txt'
            with open(file_name, 'a', newline='') as f:
                f.write(str(datetime.datetime.now()) + '\n')
                f.write(part_result + '\n\n')
                part_result = ''
                return part_result # clearing then returning pass result for next part
        else:
            part_result = part_result + str(keyence_results[0]) + ', ' # appending pass/fail data to part_result string if we're not @ end of the part
            return part_result

#START main()
def main():
    global current_stage_1 #keeps track of which stage program is currently in from the timing process
    global current_stage_2
    global kill_threads
    
    # Thread declaration / initialization
    t1 = threading.Thread(target=cycle, args=['1', current_stage_1])
    t2 = threading.Thread(target=cycle, args=['2', current_stage_2])

    t1_heartbeat = threading.Thread(target=heartbeat, args=['1'])
    t2_heartbeat = threading.Thread(target=heartbeat, args=['2'])

    kill_threads = False
    print("Starting Threads (1 & 2)...\n")
    t1.start()
    t2.start()
    #t1.join()
    #t2.join() # making sure threads complete before moving forward

    print("Starting Heartbeat Threads (1 & 2)\n")
    t1_heartbeat.start()
    t2_heartbeat.start()

    t1.join()
    t2.join()
    t1_heartbeat.join()
    t2_heartbeat.join() # joining threads to ensure synchronization if 'kill_threads' is high, all threads must end before restarting
    
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
    while(True):
        main()