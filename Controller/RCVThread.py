import threading
import json
from Model import User
from Controller import AEScipher
class RCVThread(threading.Thread):
    clientSocket = None
    BUFSIZ = 4096
    db = None
    connFlag = True
    mc = None
    user = None
    aesCipher = None

    # Constructor for RCVThread instance
    def __init__(self, threadList, clientSock, db, mc):
        threading.Thread.__init__(self)
        self.threadList = threadList
        self.clientSocket = clientSock
        self.db = db
        self.connFlag = True
        self.mc = mc
        self.aesCipher = AEScipher.AEScipher()

    # start thread
    def run(self):
        #try:
            while self.connFlag:
                msg = self.clientSocket.recv(self.BUFSIZ)
                print('Server Received:' + str(msg))
                if not msg:
                    break
                else:
                    msg = self.analyzeMsg(msg)
                    self.sendMsg(msg)
                    if msg['MSG'] == '/SLIT' or msg['MSG'] == '/LGIN':
                        mode = 'ONE'
                        if msg['MSG'] == '/SLIT':
                            mode = 'ALL'
                            print(mode)
                            self.mc.createRoomThread(self, msg['RIDX'], self.db)
                        self.sendListRef(self.mc.userList, mode)
                    elif msg['MSG'] == '/RINF':
                        self.sendImg(msg['ITPATH'])

                    elif msg['MSG'] == '/ACRQ':
                        self.sendRoomRef(self.mc.userList, msg)
        #except:
        #    self.exit()

    # analyze the message
    def analyzeMsg(self, msg):
        msgDict = self.aesCipher.decrypt(msg)
        sendDict = {'RPLY': 'REJ'}
        if msgDict['MSG'] == '/CKID':
            idBool = self.db.search(msgDict['ID'], 1)
            sendDict['MSG'] = '/CKID'
            if idBool:
                sendDict['RPLY'] = 'ACK'

        elif msgDict['MSG'] == '/LGIN':
            idBool = self.db.search(msgDict['ID'], 1)
            pwBool = self.db.search(msgDict['PW'], 2)
            sendDict['MSG'] = '/LGIN'
            if not idBool and not pwBool:
                sendDict['NAME'] = self.db.getData(msgDict['ID'], 2)
                sendDict['MONEY'] = self.db.getData(msgDict['ID'], 3)
                sendDict['RPLY'] = 'ACK'
                sendDict['ID'] = msgDict['ID']
                self.user = User.User(self.clientSocket, msgDict['ID'], sendDict['MONEY'], self.db.getData(msgDict['ID'], 1))
                self.mc.userList.append(self.user)
        elif msgDict['MSG'] == '/MAIL':
            mailBool = self.db.search(msgDict['MAIL'], 3)
            sendDict['MSG'] = '/MAIL'
            if mailBool:
                sendDict['RPLY'] = 'ACK'

        elif msgDict['MSG'] == '/SGUP':
            signUpBool = self.db.insert(msgDict, 1)
            sendDict['MSG'] = '/SGUP'
            if signUpBool:
                sendDict['NAME'] = self.db.getData(msgDict['ID'], 2)
                sendDict['MONEY'] = self.db.getData(msgDict['ID'], 3)
                sendDict['RPLY'] = 'ACK'
                sendDict['ID'] = msgDict['ID']

        elif msgDict['MSG'] == '/CHPW':
            sendDict['MSG'] = '/CHPW'
            if self.db.getData(msgDict['ID'], 4) == msgDict['CURPW']:
                chBool = self.db.updateData(msgDict['ID'], msgDict['NEWPW'], self.db.getData(msgDict['ID'], 1))
                if chBool:
                    sendDict['RPLY'] = 'ACK'

        elif msgDict['MSG'] == '/CHMN':
            curMoney = self.db.getData(msgDict['ID'], 3)
            curMoney = int(curMoney) + int(msgDict['MONEY'])
            cgBool = self.db.updateData(msgDict['ID'], curMoney, 2)
            sendDict['MSG'] = '/CHMN'
            if cgBool:
                sendDict['RPLY'] = 'ACK'
            sendDict['MONEY'] = curMoney

        elif msgDict['MSG'] == '/SLIT':
            roomBool, roomIdx, endTime = self.db.insert(msgDict, 2)
            sendDict['MSG'] = '/SLIT'
            if roomBool:
                item = self.mc.createItem(msgDict, roomIdx)
                msgDict['ITEM'] = item
                itemBool = self.db.insert(msgDict, 3)
                if itemBool:
                    sendDict['RPLY'] = 'ACK'
                    sendDict['RIDX'] = roomIdx
                    self.recvImg(item.imgPath)
                    self.mc.createRoom(roomIdx, endTime, item)

        elif msgDict['MSG'] == '/RINF':
            info = self.db.getItem(msgDict['RIDX'])
            sendDict = self.mc.createItemDict(sendDict, info)
            sendDict['RIDX'] = msgDict['RIDX']

        elif msgDict['MSG'] == '/ACRQ':
            myIdx = self.db.getData(msgDict['BUYER'], 1)
            preData = self.db.getPreBuyer(msgDict['RIDX'])

            # itname, prebuyer, msg, sgDict
            self.sendAlarm(preData[0], preData[1], '/FAILED', msgDict['PRICE'])

            rFlag = self.db.reqAuction(msgDict['RIDX'], myIdx, msgDict['PRICE'])
            if rFlag:
                sendDict['RPLY'] = 'ACK'
                sendDict['MSG'] = '/ACRQ'
                sendDict['RIDX'] = msgDict['RIDX']
                sendDict['PRICE'] = msgDict['PRICE']

        elif msgDict['MSG'] == '/ACLT':
            sendDict = self.getRoomList(msgDict, 1)

        elif msgDict['MSG'] == '/PCLT':
            sendDict = self.getRoomList(msgDict, 2)

        elif msgDict['MSG'] == '/RRRR':
            self.sendListRef(self.mc.userList, 'ONE')
            sendDict = msgDict

        else:
            pass
        return sendDict

    # receive image from client
    def recvImg(self, imgPath):
        with open(imgPath, 'wb') as f:
            while True:
                buf = self.clientSocket.recv(self.BUFSIZ)
                if str(buf[len(buf)-1]) == '96':
                    buf = bytearray(buf)
                    buf.pop(len(buf)-1)
                    buf = bytes(buf)
                    f.write(buf)
                    f.close()
                    break
                f.write(buf)

    # send message with encryption
    def sendMsg(self, msg):
        print('Server Send: '+str(msg))
        msg = str(msg)
        aesMsg = self.aesCipher.encrypt(msg)
        self.clientSocket.send(aesMsg)

    # send alarm to client who is joining in the auction
    def sendAlarm(self, buyer, itemName, msg, money=None):

        sendDict = {'MSG': '/ALRM'}
        if msg == '/SUCCESS':
            sendDict['CNT'] = 'Auction ' + itemName +' SUCCESS'
            sendDict['MONEY'] = money
            sendDict['RPLY'] = 'ACK'
        elif msg == '/FAILED':
            sendDict['CNT'] = 'Auction ' + itemName + ' FAILED'
            sendDict['RPLY'] = 'REJ'
        elif msg == '/SELLER':
            sendDict['RPLY'] = 'NON'
            sendDict['MONEY'] = money

        for i in range(len(self.mc.userList)):
            if buyer == self.mc.userList[i].myIdx:
                sendDict = str(sendDict)
                print('Server Send: ' + sendDict)
                aesMsg = self.aesCipher.encrypt(sendDict)
                self.mc.userList[i].clientSock.send(aesMsg)

    # Send image to Client
    def sendImg(self, imgPath):
        with open(imgPath, 'rb') as f:
            img = f.read()
            self.clientSocket.send(img)
            self.clientSocket.send(bytes('`', 'utf-8'))
            f.close()

    # Send room data to client
    def sendRoomRef(self, userList, sendDict):
        sendDict['MSG'] = '/RERQ'
        sendDict.pop('RPLY')
        aesMsg = self.aesCipher.encrypt(sendDict)
        for i in range(len(userList)):
            userList[i].clientSock.send(aesMsg)

    # get room list from database
    def getRoomList(self, sendDict, mode):
        sendDict['MSG'] = '/ACLT'
        myIdx = self.db.getData(sendDict['ID'], 1)
        rooms = self.db.getMyRooms(myIdx, mode)
        sendDict['ROOMS'] = self.mc.createList(rooms)
        sendDict.pop('ID')
        return sendDict

    # send room list data to client
    def sendListRef(self, userList, mode):
        sendDict = {'MSG': '/RLST'}
        rooms = self.db.getRooms(self.mc.alarmIdx)
        sendDict['ROOMS'] = self.mc.createList(rooms)
        if mode == 'ALL':
            aesMsg = self.aesCipher.encrypt(sendDict)
            for i in range(len(userList)):
                userList[i].clientSock.send(aesMsg)
        elif mode == 'ONE':
            self.sendMsg(sendDict)

    # close socket and thread
    def exit(self):
        self.connFlag = False
        self.clientSocket.close()
        self.threadList.remove(self)
        try:
            self.mc.userList.remove(self.user)
        except:
            print("No user in userList")