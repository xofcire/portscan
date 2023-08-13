#!/usr/bin/python3
'''

    Scan ports of a target IP address or hostname in a random order.

      /\---/\
     /  o o  \  Eric Fox
     \.\   /./  eric@fox.phoenix.az.us
        \@/

'''

import pyfiglet
import socket
import sys
import datetime
import random

scanned_ports   = []
ports_to_scan   = []
open_ports      = []
maximum_ports   = 65535
target          = ''
max_line_len    = 0
scan_started    = ''
scan_finished   = ''


def print_big_title(title):
    '''(str) -> int

    Print a big fancy title, return length of longest line.

    >>> print_big_title('Demo')
     ____                       
    |  _ \  ___ _ __ ___   ___  
    | | | |/ _ \ '_ ` _ \ / _ \ 
    | |_| |  __/ | | | | | (_) |
    |____/ \___|_| |_| |_|\___/ 
                            

    28

    '''
    global max_line_len
    max_length = 0
    big_banner_lines = []
    big_banner = pyfiglet.figlet_format(title)
    big_banner_lines = big_banner.split('\n')

    for i in range(len(big_banner_lines)):
        max_length = max(max_length, len(big_banner_lines[i]))

    print(big_banner)
    max_line_len = max_length

    return


def populate_ports_to_scan(maximum_ports):
    ''' (int) -> nonetype

    Update ports_to_scan with list of ports to be scanned.

    '''

    
    for i in range(maximum_ports):
        ports_to_scan.append(i + 1)

    return


def get_target():
    ''' () -> str

    Retrieve and return first system rgument to script.

    '''

    target = ''
    if sys_argument_exists():
        target = sys.argv[1]
    else:
        target = ask_for_target()

    target = socket.gethostbyname(target)

    return target


def ask_for_target():
    ''' () -> str

    Ask for the hostname or IP to target.

    '''

    target = ''
    while target == '':
        target = input('Hostname or IP address to scan: ')

    return target


def sys_argument_exists():
    ''' () -> bool

    Test if a system argument exists.

    '''

    return len(sys.argv) == 2

def print_scan_header(target):
    ''' (str) -> nonetype

    Print the scan header with horizontal lines
    the same length as the big_title.

    '''
    global scan_started
    
    scan_started = datetime.datetime.now()
    print('-' * max_line_len)
    print('Scanning Target:  ' + target)
    print('Scanning started: ' + str(scan_started))
    print('-' * max_line_len)

    return

def do_portscan(target):
    ''' (str) -> nonetype

    Port scan the target host in random,
    non-sequential manner. 
    
    '''
    global scan_finished

    while len(ports_to_scan) != 0:
        # select a port and remember what we've scanned
        this_port = random.choice(ports_to_scan)
        scanned_ports.append(this_port)
        ports_to_scan.remove(this_port)
        
        # what percentage have we scanned?
        percent = int(len(scanned_ports) / maximum_ports * 100)
        
        # print progress report
        blank_line()
        this_scan = ' Scanning Random Port:{0:>6} ({1:>3}%)'.format(this_port, percent)
        found_open = 'Number Open: {0} '.format(len(open_ports))
        num_spaces = max_line_len - len(this_scan) - len(found_open)
        this_scan = this_scan + ' ' * num_spaces + found_open
        print(this_scan, end='\r', flush=True)
        

        # test the port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = s.connect_ex((target,this_port))

        # process result of testing
        if result == 0:
            open_ports.append(this_port)
        s.close()

    scan_finished = datetime.datetime.now()

    # print final progress report
    blank_line()
    this_scan = ' Random Scan Complete  ({0:>3}%)'.format(percent)
    found_open = 'Number Open: {0} '.format(len(open_ports))
    num_spaces = max_line_len - len(this_scan) - len(found_open)
    print(this_scan + ' ' * num_spaces + found_open)

    return

def s_or_not(word, count):
    ''' (str, int) -> str

    Return the word in either singular or plural form,
    i.e., with our without the trailing "s".

    Precondition: 'word' must be in sigular format, &
    count >= 0.

    >>> s_or_not('hour', 4)
    '4 hours'
    >>> s_or_not('minute', 1)
    '1 minute'
    '''

    if count != 1:
        word = word + 's'

    return str(count) + ' ' + word
    

def print_report ():

    # print elapsed time
    print('\r' + '-' * max_line_len)
    time_diff = scan_finished - scan_started
    e_days = time_diff.days
    e_seconds_today = time_diff.seconds
    e_hours = int(e_seconds_today / 3600)
    e_minutes = int((e_seconds_today - (e_hours * 3600)) / 60)
    e_seconds = e_seconds_today - (e_hours * 3600) - (e_minutes * 60)
    elapsed_header = ' Time Elapsed: '
    elapsed_time = s_or_not('day', e_days) + ', ' + s_or_not('hour', e_hours) + ', '
    elapsed_time = elapsed_time + s_or_not('minute', e_minutes) + ', ' 
    elapsed_time = elapsed_time + s_or_not('second', e_seconds) + ' '
    num_spaces = max_line_len - len(elapsed_header) - len(elapsed_time)
    print(elapsed_header + ' ' * num_spaces + elapsed_time)

    print('\nPorts Discovered:')
    if len(open_ports) == 0:
        print(' No open ports found.')
    else:
        open_ports.sort()
        for i in range(len(open_ports)):
            print(' Port {} is open'.format(open_ports[i]))
    print('\r')
    return

def blank_line():
    ''' () -> nonetype

    Blank out the line so it can be over written without remaining artifacts.

    '''

    print('\r', end='\r',flush=True)
    print(' ' * max_line_len, end='\r', flush=True)

    return



##### Main Body #####

try:
    print('\nRandomized')
    print_big_title('Port Scanner')
    populate_ports_to_scan(maximum_ports)
    target = get_target()
    print_scan_header(target)
    do_portscan(target)
    print_report()

except KeyboardInterrupt:
    blank_line()
    print('\r ABORT: Exiting Program !!!!')
    sys.exit()
except socket.gaierror:
    blank_line()
    print(' ERROR: Hostname Could Not Be Resolved !!!!')
    sys.exit()
except socket.error:
    blank_line()
    print('\r ERROR: Server not responding !!!!')
    sys.exit()


# end
