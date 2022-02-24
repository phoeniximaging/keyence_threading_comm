import threading
import datetime, time
import socket
import csv

'''
This is the latest working example of threading communication with the Keyence (2.10.2022).

On start, creates two threads to communicate with the Livonia Keyence. Thread 1 starts (triggering Keyence), a 10 second artificial pause is called,
then Thread 2 starts to cancel the (in-progress) scan.

Thread 1: Sends 'T1' to the Keyence then reads the '%Busy' tag until LOW (scan complete)
Thread 2: Sends 'TE,0' then 'TE,1' to CANCEL the currently running scan and sets Keyence to a state that will accept a new 'T1'
'''

# global variable declarations, some are probably unnecessary(?)
trigger_count = 0
slow_count = 0
longest_time = 0

current_stage = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.83', 8500)) # 'sock' is the connection variable used to communicate with the Keyence

lock = threading.Lock()

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

# function to read in .csv file emulating plc from phoenix-101
def csv_read(io):
    #csv file reader variable declaration
    #file = open('\\phoenix-101\homes\Howard.Roush\Drive\plc_dummy.csv') #Python doesn't like \\
    #file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_dummy.csv')
    if io == 'o':
        file = open('//phoenix-101/homes/Howard.Roush/Drive/phoenix_to_plc.csv')
    if io == 'i':
        file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_to_phoenix.csv')
    csvreader = csv.reader(file)

    plc_dict = {}

    while(len(plc_dict) == 0):
        try:
            #creating two lists that will be combined in the dictionary 'plc_dict'
            header = []
            header = next(csvreader) # tag names
            values = []
            values = next(csvreader) # values

            #plc_dict = {} # dictionary: key = tag name
            #setting relevant value for each tag
            for x in range(len(header)):
                plc_dict[header[x]] = int(values[x]) #populating dict, casting to int for simplicity
                
        except Exception as e:
            print(f'EXCEPTION : {e}')

    #print(len(header))
    #print(values)

    

    #print(plc_dict)
    #print()
    #print(type(plc_dict['LOAD_PROGRAM']))
    return plc_dict
#END csv_read

# Writes back to .csv (plc) with current tag values
def csv_write(results):
    header = []
    values = []
    #file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_dummy.csv', 'w', newline='')
    file = open('//phoenix-101/homes/Howard.Roush/Drive/phoenix_to_plc.csv', 'w', newline='')
    csv_writer = csv.writer(file)

    for key in results:
        header.append(key)
        values.append(results[key])

    csv_writer.writerow(header)
    csv_writer.writerow(values)


#START main()
def main():
    global current_stage #keeps track of which stage program is currently in from the timing process

    while(True):
        #reading in .csv plc emulator for initial values
        #split into two .csv files, representing each direction of traffic between PLC and Phoenix
        csv_results = csv_read('o') #holds PHOENIX tags / data
        csv_results_plc = csv_read('i') #holds PLC (Grob) tags / data

        #STAGE0 CHECK HERE
        if(current_stage == 0):
            time.sleep(1)
            print('Stage 0 : Listening for PLC(LOAD_PROGRAM) = 1')
            #reading .csv until LOAD_PROGRAM goes high
            while(csv_results_plc['LOAD_PROGRAM'] != 1):
                csv_results_plc = csv_read('i')
                #print(csv_results)
                time.sleep(1)

            print('PLC(LOAD_PROGRAM) went high!')
            # Once PLC(LOAD_PROGRAM) goes high, mirror data and set Phoenix(READY) high, signifies end of "loading" process
            csv_results['READY'] = 0 # LOAD is high, so READY goes low
            csv_write(csv_results)
            print('Dropping Phoenix(READY) low.')

            #TODO Send branch data to load Keyence for scan
            LoadKeyence(sock,'MW,#PhoenixControlFaceBranch,2\r\n') #example message with branch#2 passed into Keyence
            print('Keyence Loaded!')

            #TODO Actually Mirror Data (write back to PLC)
            print('!Mirroring Data!')
            csv_results['DATA'] = csv_results_plc['DATA']
            #time.sleep(3) #artificial pause to see step happening in testing
            print('Data Mirrored, Setting \'READY\' high')

            csv_results['READY'] = 1
            csv_write(csv_results)
            time.sleep(3)
            current_stage += 1 #incrementing out of STAGE0
        #END STAGE0
        #START STAGE1 : START/END Program
        elif(current_stage == 1):
            print('Stage 1!\nListening for PLC(START_PROGRAM) = 1')
            time.sleep(3)
            if(csv_results_plc['START_PROGRAM'] == 1):
                print('PLC(START_PROGRAM) went high! Time to trigger Keyence...')
                #TODO TRIGGER KEYENCE
                csv_results['BUSY'] = 1
                csv_write(csv_results)
                #TODO Actual Keyence Trigger (T1) here***
                TriggerKeyence(sock, 'T1\r\n')

                # Pretend to scan if Keyence not available
                #print('PHOENIX(BUSY) is high...pretend scanning here')
                time.sleep(5)

                csv_results['BUSY'] = 0
                csv_write(csv_results)
                print('Pretend scan ended! PHOENIX(BUSY) is low')
                #TODO PASS/FAIL RESULTS
                print('*This is where PASS/FAIL data would be written out*')
                print('PHOENIX(DONE) = 1')
                csv_results['DONE'] = 1
                csv_results['DATA'] = 0
                csv_write(csv_results)
                print('Stage 1 Complete!')
                current_stage += 1
                time.sleep(3)
            
        #Final Stage, reset to Stage 0 once PLC(END_PROGRAM) and PHOENIX(DONE) have been set low
        elif(current_stage == 2):
            print('Stage 2 : Listening to PLC(END_PROGRAM) high to reset back to Stage 0')
            if(csv_results_plc['END_PROGRAM'] == 1):
                print('PLC(END_PROGRAM) is high. Dropping PHOENIX(DONE) low')
                csv_results['DONE'] = 0
                csv_write(csv_results)
                current_stage = 0
                
            '''
            if(csv_results_plc['END_PROGRAM'] == 0 and csv_results['DONE'] == 0):
                print('PLC(END_PROGRAM) is low. Resetting PHOENIX to Stage 0')
                current_stage = 0 # cycle complete, reset to stage 0
            '''
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