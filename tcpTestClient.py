import socket
import struct
import time
import threading
import pickle
import matplotlib.pyplot as plt
import numpy as np


address = '192.168.178.36'
address = '192.168.1.121'
port = 21292

  #Befehle
CMD_ECHO = 0x0001
CMD_START_DATA_TRANSFER = 0x0002
CMD_STOP_DATA_TRANSFER = 0x0003
CMD_RESET_RADAR_COUNTER = 0x0004
CMD_DISCOVERY = 0x0005
 
  #Antworten
CMD_ANSWER_OK = 0x8000
CMD_ANSWER_ERROR = 0x8001
CMD_START_TRANSFER_ACCEPTED = 0x8002
CMD_START_TRANSFER_REFUSED = 0x8003
CMD_DISCOVERY_ANSWER = 0x8004
CMD_DATA_TRANSFER_STOPPED = 0x8005

def send(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    cnt = s.send(cmd)
    print(f'{cnt} Bytes gesendet')

def sendEchoCmd(cmd):
    assert cmd[0] == 1 and cmd[1] == 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    cnt = s.send(cmd)
    print(f'{cnt} Bytes gesendet')
    buff = s.recv(1000)
    print(f'received:\n {buff[4:]}')
    s.close()

def sendResetRadarCntCmd(pulsesPerMeter, datasetsPerMeter):
    cmd = struct.pack('=hhfh', CMD_RESET_RADAR_COUNTER, struct.calcsize('fh'), pulsesPerMeter, datasetsPerMeter )
    send(cmd)

def sendStopDataTransferCmd():
    cmd = struct.pack('=hh', CMD_STOP_DATA_TRANSFER, 0 )
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    cnt = s.send(cmd)
    print(f'{cnt} Bytes gesendet')
    buff =s.recv(1000)
    id, sz = struct.unpack('=HH', buff[0:4])
    assert id == CMD_DATA_TRANSFER_STOPPED
    s.close()

def sendDiscoveryCmd():
    udpPort = 21293
    addresses = ['192.168.1.255', '192.168.178.255']
    for address in addresses:
        try:
            cmdParams = "LSE-MMXX-controller?".encode()
            #print(cmdParams)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            fmt = f'=hh{len(cmdParams)}s'
            cmd = struct.pack(fmt, CMD_DISCOVERY, len(cmdParams), cmdParams)
            print(cmd)
            
            cnt = s.sendto(cmd, (address, udpPort))
            print(f'{cnt} Bytes gesendet')
            #return
            
            recData =b''
            recData, sender = s.recvfrom(1000)
            print(recData)
            answ = recData[4:].decode()
            print(f'received: {recData}')
            uCip, ucPort = answ.split(':') 
            ucPort = int(ucPort)
            print(f'uC Adresse: {uCip}:{ucPort}')
        except socket.timeout as exc:
            print(f'discover timeout for {address}')

def searchArduino():
    udpPort = 21293
    addresses = ['192.168.1.255', '192.168.178.255', '192.168.2.255']
    for address in addresses:
        try:
            cmdParams = "LSE-MMXX-controller?".encode()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            fmt = f'=hh{len(cmdParams)}s'
            cmd = struct.pack(fmt, CMD_DISCOVERY, len(cmdParams), cmdParams)
            cnt = s.sendto(cmd, (address, udpPort))
            recData =b''
            recData, sender = s.recvfrom(1000)
            answ = recData[4:].decode()
            uCip, ucPort = answ.split(':') 
            ucPort = int(ucPort)
            print(f'uC found: {uCip}:{ucPort}')
            return uCip, ucPort
        except socket.timeout as exc:
            pass

timestamps = []
radar = []
speed = []
dsCnt = []
periodDuration = []
a0a2 = []
a3a5 = []
WireSensor =[]

dataTransfSocket = None
def startDataTransfer():
    def datTransferFun():
        fmt = f'=hh'
        cmd = struct.pack(fmt, CMD_START_DATA_TRANSFER, 0)
        dataTransfSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataTransfSocket.connect((address, port))
        cnt = dataTransfSocket.send(cmd)
        print(f'{cnt} Bytes gesendet')
        try:
            buff = b''
            BUFF_SZ = 2048
            recBuff = dataTransfSocket.recv(BUFF_SZ)
            cmdResponse = recBuff[0:4]
            response = struct.unpack('2H', cmdResponse)
            if response[0] != CMD_START_TRANSFER_ACCEPTED:
                print('Verbindung wurde nicht akzeptiert')
                return
            buff += recBuff[4:]
            while recBuff:
                #print(f"Empfangsbuffergröße: {len(recBuff)}")
                #data = struct.unpack(fmt, buff)
                #print(data)
                recBuff = dataTransfSocket.recv(BUFF_SZ)
                buff += recBuff
                fmt = 'IfIf2I'
                fmtSz = struct.calcsize(fmt)
                while len(buff) >= fmtSz:
                    data = struct.unpack(fmt, buff[0:fmtSz])
                    buff = buff[fmtSz:]
                    print(f'{data[0]} {data[1]} {data[2]} {data[3]}')
                    offset = 0
                    #timestamps.append(data[offset])
                    #offset += 1
                    ########################################
                    #radar.append(data[offset])
                    #offset += 1
                    #speed.append(data[offset])
                    #offset += 1
                    #dsCnt.append(data[offset])
                    #offset += 1
                    #periodDuration.append(data[offset])
                    #offset += 1
                    #a0a2.append(data[offset])
                    #offset += 1
                    #a3a5.append(data[offset])
                    #offset += 1
                    ##################################################
                    speed.append(data[offset])
                    offset += 1
                    WireSensor.append(data[offset])
                    offset += 1
                    a0a2.append(data[offset])
                    offset += 1
                    a3a5.append(data[offset])
                    offset += 1
                    #packed_value = a0a2[0]
                    #ma0 = packed_value & 0x03FF  # Extract first 10 bits
                    #ma1 = (packed_value >> 10) & 0x03FF  # Extract the next 10 bits
                    #ma2 = (packed_value >> 20) & 0x03FF  # Extract the last 10 bits
                    #packed_value2 = a3a5[0]
                    #ma3 = packed_value2 & 0x03FF  # Extract first 10 bits
                    #ma4 = (packed_value2 >> 10) & 0x03FF  # Extract the next 10 bits
                    #ma5 = (packed_value2 >> 20) & 0x03FF  # Extract the last 10 bits
                    #print(f' {ma0} {ma1} {ma2} {ma3} {ma4} {ma5}')


        except Exception as exc:
            print(exc)

    th = threading.Thread( target = datTransferFun)
    th.start()

def stopDataTransfer():
    fmt = f'=hh'
    cmd = struct.pack(fmt, CMD_STOP_DATA_TRANSFER, 0)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    cnt = s.send(cmd)
    print(f'{cnt} Bytes gesendet')
    if dataTransfSocket:
        dataTransfSocket.close()


def tests():
    buff = 'In principio erat verbum'.encode()
    buffSz = len(buff)
    fmt = f'=hh{buffSz}b'
    print(f'format: {fmt}')

    cmd = struct.pack(fmt, CMD_ECHO, buffSz, *buff)
    print(cmd)
    for i in range(20):
        print(i)
        sendEchoCmd(cmd)

def _saveData():
    with open('data.bin', 'wb') as fd:
        pickle.dump(timestamps, fd)
        pickle.dump(radar, fd)
        pickle.dump(dsCnt, fd)
        pickle.dump(periodDuration, fd)
        pickle.dump(a0a2, fd)
        pickle.dump(a3a5, fd)
        pickle.dump(speed, fd)

def dataAnalysis():
    ts = []
    r = []
    dsCnt = []
    dur = []
    a0a2 = []
    a3a5 = []
    sp = []
    with open('data.bin', 'rb') as fd:
        ts = pickle.load(fd)
        r = pickle.load(fd)
        dsCnt = pickle.load(fd)
        dsCnt = np.array(dsCnt)
        dur = pickle.load(fd)
        a0a2 = pickle.load(fd)
        a3a5 = pickle.load(fd)
        sp = pickle.load(fd)

    a0 = []
    a1 = []
    a2 = []
    for a in a0a2:
        a0.append(a & 0x03ff)
        a1.append((a >> 10) & 0x03ff)
        a2.append((a >> 20) & 0x03ff)

    a3 = []
    a4 = []
    a5 = []
    for a in a3a5:
        a3.append(a & 0x03ff)
        a4.append((a >> 10) & 0x03ff)
        a5.append((a >> 20) & 0x03ff)

    a0 = np.array(a0)
    a1 = np.array(a1)
    a2 = np.array(a2)
    a3 = np.array(a3)
    a4 = np.array(a4)
    a5 = np.array(a5)

    arr = np.roll(dsCnt, 1)
    arr[0] = dsCnt[0]

    # plt.plot(dsCnt - arr)
    # missing = dsCnt - arr - 1 #minus 1 weil Änderung um 1 muss sein
    # missing = (np.sum(missing))
    # print(f'missing: {missing}')

    #plt.plot(sp)

    time = np.array(dur)
    for i in range(1,len(time)):
        time[i] = time[i] + time[i-1]
    plt.plot(time, a0 / 1024.0 * 5.0, label = "A0")
    plt.plot(time, a1 / 1024.0 * 5.0, label = "A1")
    plt.plot(time, a2 / 1024.0 * 5.0, label = "A2")
    plt.plot(time, a3 / 1024.0 * 5.0, label = "A3")
    plt.plot(time, a4 / 1024.0 * 5.0, label = "A4")
    plt.plot(time, a5 / 1024.0 * 5.0, label = "A5")
    plt.xlabel('t[ms]')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    # for i in range(1): 
    #     pass
    #     sendDiscoveryCmd()
    address, port = searchArduino() 
    #tests()
    #sendEchoCmd(CMD_ECHO)
    # exit()
    #for i in range(10):
    #    sendStopDataTransferCmd()
    #    pass
    #exit()
    #dataAnalysis()
    #exit()
    #tests()
    #exit()
    #sendResetRadarCntCmd(10, 4)
    #exit()
    startDataTransfer()
    time.sleep(5000)
    #stopDataTransfer()
    #_saveData()
    #dataAnalysis()
