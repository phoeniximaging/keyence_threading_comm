import threading
import datetime, time
import socket
import csv

'''
This testing program is used to send and recv a single message from one Keyence unit
'''

# global variable declarations, some are probably unnecessary(?)
trigger_count = 0
slow_count = 0
longest_time = 0
shortest_time = 100
current_stage = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.83', 8500)) # 'sock' is the connection variable used to communicate with the Keyence (Livonia)
#sock.connect(('172.19.147.82', 8500))

lock = threading.Lock()

# Triggering Keyence with socket only being connected/closed ONCE (program startup and shutdown)
def TriggerKeyence(sock, machine_num, item):

    global trigger_count
    global slow_count
    global longest_time
    global start_timer_END

    #verify Keyence(Trg1Ready) is high before we send a 'T1' trigger
    with lock:
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
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print(f'({machine_num}) TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.005) # artificial 1ms pause between Keyence reads

    message = item
    trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
    with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'({machine_num}) received "%s"\n' % data)
        #start_timer_END = datetime.datetime.now() # END test timer
    #time_diff = (start_timer_END - start_timer)
    #execution_time = time_diff.total_seconds() * 1000
    #print(f'PLC(Start) read to Keyence(T1) read in : {execution_time} ms')

    #am I using these right?(!)
    with lock:
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
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print(f'({machine_num}) TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.005) # artificial 1ms pause between Keyence reads
    #print('Keyence %Trg1Ready verified!')
    trigger_end_time = datetime.datetime.now() # marking when '%BUSY' is read off Keyence
    time_diff = (trigger_end_time - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    print(f'\n({machine_num}) \'T1\' sent to \'%Trg1Ready\' verified in {execution_time} ms\n')
#END 'TriggerKeyence'

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

def KeyenceTester(sock):
    message = 'OW,42,"LOL015365G011712696498GR800-CoverFace-2-625T-10Largest.csv' # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        data = sock.recv(32)
        print(f'{data}')
    time.sleep(3)
    message = 'OW,43,"LOL015365G011712696498GR800-CoverFace-2-625T-10Largest.csv' # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        data = sock.recv(32)
        print(f'{data}')

#START main()
def main():
    global current_stage #keeps track of which stage program is currently in from the timing process
    global longest_time
    global shortest_time

    KeyenceTester(sock)
    time.sleep(100)

    #test_msg = 'MW,#PhoenixControlFaceBranch,2\r\n' #test LOAD msg
    #test_msg = 'STW,0,"LOL123ABCDBLAHBLAH***-CoverFace-2-625T\r\n' #test LOAD msg
    test_msg = 'T1\r\n'
    #test_msg = 'PR\r\n'
    while(True):
        start_timer = datetime.datetime.now()
        TriggerKeyence(sock,'123',test_msg)
        end_timer = datetime.datetime.now()
        time_diff = (end_timer - start_timer)
        execution_time = time_diff.total_seconds() * 1000
        print(f'Execution time: {round(execution_time,2)} ms\n')
        if(execution_time > longest_time):
            longest_time = execution_time
        if(execution_time < shortest_time):
            shortest_time = execution_time
        print(f'Longest Execution Time: {longest_time}\n')
        print(f'Shortest Execution Time: {shortest_time}\n')
        time.sleep(7) # artificial pause to pretend PLC sends 'EndScan' after ~7 seconds

        ExtKeyence(sock)
        time.sleep(1)

    ''' Probably won't be used for this testing program
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
    '''
#END 'main'

#implicit 'main()' declaration
if __name__ == '__main__':
    for x in range(20):
        print(f'Main Loop {x}')
        main()
        #time.sleep(3) # time between cycles to eyeball if multiple scans are actually taking place