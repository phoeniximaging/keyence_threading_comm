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
#END 'TriggerKeyence'

#START main()
def main():
    global current_stage #keeps track of which stage program is currently in from the timing process

    #test_msg = 'MW,#PhoenixControlFaceBranch,2\r\n' #test LOAD msg
    #test_msg = 'STW,0,"LOL123ABCDBLAHBLAH***-CoverFace-2-625T\r\n' #test LOAD msg
    test_msg = 'T1\r\n'
    TriggerKeyence(sock,test_msg)
    time.sleep(30)

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
    for x in range(3):
        print(f'Main Loop {x}')
        main()
        #time.sleep(3) # time between cycles to eyeball if multiple scans are actually taking place