
#import os
import csv
#import json
#import demo
import ipaddress

import sys


def getMAC(addr):
    '''
    @params: addr -- full 32-hex digit EUI-64 address
    @returns: de-localized MAC address (unless explicit deloc=False in call)
    '''
    lower64 = addr.split(':')[4:]
    one_two = lower64[0][:2] + ':' + lower64[0][2:]
    three = lower64[1][:2]
    four = lower64[2][2:]
    five_six = lower64[3][:2] + ':' + lower64[3][2:]

    return delocalize(':'.join([one_two,three,four,five_six]))

def delocalize(mac):
    '''
    @param:  mac: MAC address string of the form (xy:xx:xx:xx:xx:xx) where the
    y position has the local bit on
    @returns: delocalized mac address string
    '''
    first_byte = mac.split(':')[0]
    first_nybble = first_byte[0]
    second_nybble = first_byte[1]

    #if this is global already, return
    if not (int(second_nybble,16) >> 1) & 1:
        return mac

    second_nybble = hex(int(second_nybble,16) ^ 0x2)[2:]
    if second_nybble ==2:
        sys.exit(1)
    first_byte = first_nybble + second_nybble

    return first_byte + ':' + ':'.join(mac.split(':')[1:])


total = 0
EUI = 0
hitlist_file = "hitlist.txt" #输入
result_file = "EUI64.csv" #输出
with open(hitlist_file, "r",newline="") as read_file:
    with open(result_file, "w",newline="",encoding="gb18030") as csv_file:
        writer = csv.writer(csv_file)
        for ip in read_file:
            total += 1
            if ip.find(':') != -1:
                ip = ip.replace('\r','').replace('\n','')
                hextets = ip.split(':')
                if hextets[-3].endswith('ff') and hextets[-2].startswith('fe'):
                #if ip.find('ff:fe') != -1:
                    mac = getMAC(ipaddress.IPv6Address(ip).exploded)
                    writer.writerow([ip,mac])
                    EUI += 1
print('Total:',total,'EUI:',EUI)
