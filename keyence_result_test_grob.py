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
#sock.connect(('192.168.1.83', 8500)) # 'sock' is the connection variable used to communicate with the Keyence (Livonia)
sock.connect(('172.19.147.82', 8500))

lock = threading.Lock()

# Printing Result Info
def TriggerKeyence(sock):

    global trigger_count
    global slow_count
    global longest_time
    global start_timer_END

    result_messages = ['MR,#ReportDefectCount\r\n', 'MR,#ReportLargestDefectSize\r\n', 'MR,#ReportLargestDefectZoneNumber\r\n', 'MR,#ReportPass\r\n', 'MR,#ReportFail\r\n']
    results = []

    # sending result messages to Keyence, then cleaning results to 'human-readable' list
    for msg in result_messages:
        sock.sendall(msg.encode())
        data = sock.recv(32)
        keyence_value_raw = str(data).split('.')
        keyence_value_raw = keyence_value_raw[0].split('+')
        print(keyence_value_raw)
        keyence_value = int(keyence_value_raw[1])
        results.append(keyence_value)

    print(results)
#END 'TriggerKeyence'

#START main()
def main():
    global current_stage #keeps track of which stage program is currently in from the timing process
    global longest_time
    global shortest_time

    #test_msg = 'MW,#PhoenixControlFaceBranch,2\r\n' #test LOAD msg
    #test_msg = 'STW,0,"LOL123ABCDBLAHBLAH***-CoverFace-2-625T\r\n' #test LOAD msg
    test_msg = 'T1\r\n'
    #test_msg = 'PR\r\n'

    TriggerKeyence(sock)


#END 'main'

#implicit 'main()' declaration
if __name__ == '__main__':
    main()