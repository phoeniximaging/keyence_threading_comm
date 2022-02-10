import threading
import datetime, time
import socket

'''
This is the latest working example of threading communication with the Keyence (2.10.2022).

On start, creates two threads to communicate with the Livonia Keyence. Thread 1 starts (triggering Keyence), a 10 second artificial pause is called,
then Thread 2 starts to cancel the (in-progress) scan.

Thread 1: Sends 'T1' to the Keyence then reads the '%Busy' tag until LOW (scan complete)
Thread 2: Sends 'TE,0' then 'TE,1' to CANCEL the currently running scan and sets Keyence to a state that will accept a new 'T1'
'''

# global variable declarations
trigger_count = 0
slow_count = 0
longest_time = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.83', 8500))

lock = threading.Lock()

# Triggering Keyence with socket only being connected/closed ONCE (program startup and shutdown)
def TriggerKeyence(sock, item):

    global trigger_count
    global slow_count
    global longest_time

    try:
        message = item
        trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
            print('received "%s"' % data)

        #am I using these right?(!)
        with lock:
            message = 'MR,%Busy\r\n'
            sock.sendall(message.encode())
            data = sock.recv(32)
            #print(data)
        trigger_end_time = datetime.datetime.now() # marking when '%Busy' is read off Keyence
        time_diff = (trigger_end_time - trigger_start_time)
        execution_time = time_diff.total_seconds() * 1000
        print(f'\n\'T1\' sent to \'%Busy\' read in: {execution_time} ms')
        if(execution_time > longest_time):
            longest_time = execution_time

        # looping until busy on Keyence is low (0)
        while(data != b'MR,+0000000000.000000\r'):
            # utilizing 'with' to use thread lock
            with lock:
                message = 'MR,%Busy\r\n'
                sock.sendall(message.encode())
                data = sock.recv(32)
                print('TriggerKeyence: received "%s"' % data)
            #print('Scanning...')
            time.sleep(.5)

    finally:
        pass
        #print()

# sends 'TE,0' then 'TE,1' to the Keyence
def ExtKeyence(sock, item, item_reset):
    try:
        message = item
        with lock:
            sock.sendall(message.encode()) # sending TE,0
            print('\n\'TE,0\' Sent!')

            message = item_reset
            sock.sendall(message.encode()) # sending, TE,1
            print('\'TE,1\' Sent!')

            data = sock.recv(32)
            #print('received "%s"' % data)
    finally:
        #print()
        pass


#START main()
def main():
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


#implicit 'main()' declaration
if __name__ == '__main__':
    for x in range(3):
        print(f'Main Loop {x}')
        main()
        time.sleep(3)