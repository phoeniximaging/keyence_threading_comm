import time
import datetime

while(True):
    start_timer = datetime.datetime.now()
    for x in range(10):
        print(f'Test Print {x}')
    end_timer = datetime.datetime.now()
    time_diff = (end_timer - start_timer)
    execution_time = time_diff.total_seconds() * 1000
    print(f'Execution Time (10 prints) : {execution_time}')

    time.sleep(10)

    start_timer = datetime.datetime.now()
    for x in range(100):
        print(f'Test Print {x}')
    end_timer = datetime.datetime.now()
    time_diff = (end_timer - start_timer)
    execution_time = time_diff.total_seconds() * 1000
    print(f'Execution Time (100 prints) : {execution_time}')

    time.sleep(10)

    start_timer = datetime.datetime.now()
    for x in range(1000):
        print(f'Test Print {x}')
    end_timer = datetime.datetime.now()
    time_diff = (end_timer - start_timer)
    execution_time = time_diff.total_seconds() * 1000
    print(f'Execution Time (1000 prints) : {execution_time}')

    time.sleep(10)