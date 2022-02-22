import threading
import datetime, time
import socket
import csv
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import json
import os

'''
This is the first testing thread for Elwema using threading and an all-in-one Python program.

Progresses through the timing diagram based on tag values read off Elwema's PLC. Loads and Triggers Keyence.
'''

trigger_count = 0
slow_count = 0
longest_time = 0

current_stage = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(('192.168.1.83', 8500)) # 'sock' is the connection variable used to communicate with the Keyence
sock.connect(('172.19.147.82', 8500)) # GROB address, Keyence head #1

lock = threading.Lock()

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
    'PLANTCODE',
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
#END read_plc_dict

#Writing back to PLC to mirror data on LOAD
#TODO: Modify to use running values instead of relying on reads from an OPC server
def write_plc(plc, machine_num, results):
    #logging how long the 'read' takes
    start_time = datetime.datetime.now()

    plc.write(('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PartType', results['PartType'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PartProgram', results['PartProgram'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.ScanNumber', results['ScanNumber'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PUN{64}', results['PUN'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.GMPartNumber{8}', results['GMPartNumber'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.Module', results['Module'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PlantCode', results['PlantCode'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.Month', results['Month'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.Day', results['Day'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.Year', results['Year'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.Hour', results['Hour'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.Minute', results['Minute'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.Second', results['Second'][1])
    )

    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print('\'plc.write()\' took %d ms to run' % (execution_time))
    #print("Finished writing PLC...")
    pass
#END write_plc

# Triggering Keyence with socket only being connected/closed ONCE (program startup and shutdown)
def TriggerKeyence(sock, item):

    global trigger_count
    global slow_count
    global longest_time

    message = item
    trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
    with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print('received "%s"' % data)

    #am I using these right?(!)
    with lock:
        message = 'MR,%Busy\r\n' #initial read of '%Busy' to ensure scan is actually taking place (%Busy == 1)
        sock.sendall(message.encode())
        data = sock.recv(32)
        #print(data)
    trigger_end_time = datetime.datetime.now() # marking when '%Busy' is read off Keyence
    time_diff = (trigger_end_time - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    print(f'\n\'T1\' sent to \'%Busy\' read in: {execution_time} ms')
    if(execution_time > longest_time):
        longest_time = execution_time

    # looping until '%Busy' == 0
    while(data != b'MR,+0000000000.000000\r'):
        # utilizing 'with' to use thread lock
        message = 'MR,%Busy\r\n'
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print('TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.5)
#END 'TriggerKeyence'

#sends specific Keyence Program (branch) info to pre-load/prepare Keyence for Trigger(T1)
def LoadKeyence(sock, item):
    print('LOADING KEYENCE')
    message = item # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        print(f'\n\'{item}\' Sent!')
        data = sock.recv(32)
        print('received "%s"' % data)

# sends 'TE,0' then 'TE,1' to the Keyence, resetting to original state (ready for new 'T1')
def ExtKeyence(sock, item, item_reset):
    message = item # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        print('\n\'TE,0\' Sent!')

        message = item_reset # setting 'TE,1' to reset
        sock.sendall(message.encode()) # sending, TE,1
        print('\'TE,1\' Sent!')

        #data = sock.recv(32)
        #print('received "%s"' % data)
# END 'ExtKeyence'

#START main()
def main():
    global current_stage #keeps track of which stage program is currently in from the timing process

    print("Connecting to PLC")
    with LogixDriver('120.123.230.39/0') as plc:
        while(True):
            #reading in .csv plc emulator for initial values
            #split into two .csv files, representing each direction of traffic between PLC and Phoenix
            #csv_results = csv_read('o') #holds PHOENIX tags / data
            #csv_results_plc = csv_read('i') #holds PLC (Grob) tags / data
            csv_results = {}

            results_14_dict = read_plc_dict(plc, '1') #initial PLC tag read for 'robot 14' values
            print(results_14_dict['LOAD_PROGRAM'][1]) #how to print the value of one specific tag

            #STAGE0 CHECK HERE
            if(current_stage == 0):
                print('Stage 0 : Listening for PLC(LOAD_PROGRAM) = 1')
                #reading PLC until LOAD_PROGRAM goes high
                while(results_14_dict['LOAD_PROGRAM'][1] != True):
                    results_14_dict = read_plc_dict(plc, '1') # continuous PLC read
                    #print(csv_results)
                    time.sleep(1)

                print('PLC(LOAD_PROGRAM) went high!')
                # Once PLC(LOAD_PROGRAM) goes high, mirror data and set Phoenix(READY) high, signifies end of "loading" process
                plc.write('Program:CM080CA01.PorosityInspect.CAM01.I.READY', False)
                print('Dropping Phoenix(READY) low.')

                ''' 
                *Part Program Table:*
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
                #TODO Send branch data to load Keyence for scan
                LoadKeyence(sock,'MW,#PhoenixControlFaceBranch,' + str(results_14_dict['PART_PROGRAM'][1]) + '\r\n') #Keyence loading message, uses PartProgram from PLC to load specific branch
                print('Keyence Loaded!')

                #TODO Actually Mirror Data (write back to PLC)
                print('!Mirroring Data!')
                write_plc(plc,'14',results_14_dict) #writing back mirrored values to PLC to confirm LOAD has been processed / sent to Keyence
                #csv_results['DATA'] = csv_results_plc['DATA']
                time.sleep(1) #artificial pause to see step happening in testing
                print('Data Mirrored, Setting \'READY\' high')
                plc.write('Program:CM080CA01.PorosityInspect.CAM01.I.READY', True)
                time.sleep(3)
                current_stage += 1 #incrementing out of STAGE0
            #END STAGE0
            #START STAGE1 : START/END Program
            elif(current_stage == 1):
                print('Stage 1!\nListening for PLC(START_PROGRAM) = 1')
                time.sleep(.01) #10ms artificial delay for testing
                if(results_14_dict['START_PROGRAM'][1] == True):
                    print('PLC(START_PROGRAM) went high! Time to trigger Keyence...')
                    plc.write('Program:CM080CA01.PorosityInspect.CAM01.I.BUSY', True) #Busy goes HIGH while Keyence is scanning

                    #Actual Keyence Trigger (T1) here***
                    TriggerKeyence(sock, 'T1\r\n')

                    print('Pretend scan ended! PHOENIX(BUSY) is low')
                    plc.write('Program:CM080CA01.PorosityInspect.CAM01.I.BUSY', False)

                    #TODO PASS/FAIL RESULTS
                    print('PASS/FAIL/DONE data written out')
                    plc.write(('Program:CM080CA01.PorosityInspect.CAM01.I.PASS', True),
                    'Program:CM080CA01.PorosityInspect.CAM01.I.DONE', True)
                    print('PHOENIX(PASS) and PHOENIX(DONE) = 1')
                    print('Stage 1 Complete!')
                    current_stage += 1
                    time.sleep(1)
                
            #Final Stage, reset to Stage 0 once PLC(END_PROGRAM) and PHOENIX(DONE) have been set low
            elif(current_stage == 2):
                done_check = plc.read('Program:CM080CA01.PorosityInspect.CAM01.I.DONE')
                print('Stage 2 : Listening to PLC(END_PROGRAM) low to reset back to Stage 0')
                if(results_14_dict['END_PROGRAM'][1] == True):
                    print('PLC(END_PROGRAM) is high. Dropping PHOENIX(DONE) low')
                    plc.write('Program:CM080CA01.PorosityInspect.CAM01.I.DONE', False)
                    
                if(results_14_dict['END_PROGRAM'][1] == False and done_check[1] == False):
                    print('PLC(END_PROGRAM) is low. Resetting PHOENIX to Stage 0')
                    current_stage = 0 # cycle complete, reset to stage 0
                
                time.sleep(1)


    #BEGIN THREADING TRIGGER KEYENCE
    #declaring threads, does not run
    t1 = threading.Thread(target=TriggerKeyence, args=[sock, 'T1\r\n']) #thread1, passing in socket connection and 'T1' keyence command
    t2 = threading.Thread(target=ExtKeyence, args=[sock, 'TE,0\r\n', 'TE,1\r\n']) #thread2, uses 'TE,0' and 'TE,1' to cancel while scanning and reset to original state

    #starting threads
    t1.start()
    #t1.join() #'join' locks until the thread has processed (?)

    #waits 10 seconds while 'T1' starts / is scanning
    for x in range (10):
        print(x)
        time.sleep(1)

    # starts second thread to send 'TE,0' and 'TE,1' to Keyence, cancelling the current scan in progress and resetting Keyence to a state that will accept a new 'T1'
    t2.start()
    t2.join() #! will this keep thread ordered between calls to main()?

    print(f'\n*Longest Time*: {longest_time}\n')
    #print('End main()')
#END 'main'

#implicit 'main()' declaration
if __name__ == '__main__':
    for x in range(1000):
        print(f'Main Loop {x}')
        main()
        #time.sleep(3) # time between cycles to eyeball if multiple scans are actually taking place