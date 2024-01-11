'''
Mason Adsero
fxp_bytes_subscriber.py
10 24 2022
'''
import socket
import ipaddress
from array import array
import datetime

#consulted Justin for line with message = bytes
@staticmethod
def serialize_addr(addr, sockinfo):
    '''
    this function serializes the information we send to subscribe to the publish.
    this includes our ip, and port.
    :param sockinfo: Holds our ip address and port number
        message: returns our serialized message
    '''
    hostIp = sockinfo[0]
    hostIp = hostIp.split(".")
    tmp = []
    for num in hostIp:
        tmp.append(int(num))
    hostIp = tmp
    port = [sockinfo[1]]
    port = array('H', port)
    port.byteswap()
    message = bytes([*hostIp, *port.tobytes()])
    return message

def unmarshal(data):
    '''
    This function unmarshals quotes from the publisher and converts everything to the correct type for our machine
    :param data: The quote in bytes from the publisher
        retuns a tuple of time, the currencies, and the exchangerate as the quote
    '''
    time = array('Q')
    time.frombytes(data[0:8])
    time.byteswap() # little endian
    epoch = datetime.datetime(1970, 1, 1)
    time = epoch + datetime.timedelta(microseconds=time[0])
    currOne = data[8:11].decode('utf-8')
    currTwo = data[11:14].decode('utf-8')
    exchRate = array('d')
    exchRate.frombytes(data[14:22])
    exchRate = exchRate[0]
    return (time, currOne, currTwo, exchRate)