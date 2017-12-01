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
    server = None

    # Constructor for RCVThread instance
    def __init__(self,server, threadList, clientSock, db, mc):
        self.server = server
        threading.Thread.__init__(self)
        self.threadList = threadList
        self.clientSocket = clientSock
        self.db = db
        self.connFlag = True
        self.mc = mc
        self.aesCipher = AEScipher.AEScipher()

    # start thread
    def run(self):
        try:
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
                            self.mc.createRoomThread(self, msg['RIDX'], self.db)
                        self.sendListRef(self.mc.userList, mode)
                    elif msg['MSG'] == '/RINF':
                        self.sendImg(msg['ITPATH'])
                    elif msg['MSG'] == '/ACRQ':
                        self.sendRoomRef(self.mc.userList, msg)
                    elif msg['MSG'] == '/WCLT' and msg['RPLY'] == 'ACK':
                        roomList = msg['ROOMS']
                        for i in range(len(roomList)):
                            self.sendImg(roomList[i][1])
        except:
            self.exit()

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
                myIdx = self.db.getData(msgDict['ID'], 3)
                sendDict['MONEY'] = self.db.getData_Index(myIdx, 2)
                sendDict['NAME'] = self.db.getData_Index(myIdx, 3)
                lFlag = True
                for i in range(len(self.mc.userList)):
                    if myIdx == self.mc.userList[i].myIdx:
                        lFlag = False
                        break
                if lFlag:
                    sendDict['RPLY'] = 'ACK'
                    sendDict['ID'] = msgDict['ID']
                    self.user = User.User(self.clientSocket, msgDict['ID'], sendDict['MONEY'], myIdx)
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
                sendDict['RPLY'] = 'ACK'

        elif msgDict['MSG'] == '/CHPW':
            sendDict['MSG'] = '/CHPW'
            if self.db.getData_Index(self.user.myIdx, 1) == msgDict['CURPW']:
                chBool = self.db.updateData(self.user.myIdx, msgDict['NEWPW'], 1)
                if chBool:
                    sendDict['RPLY'] = 'ACK'

        elif msgDict['MSG'] == '/CHMN':
            curMoney = self.db.getData_Index(self.user.myIdx, 2)
            curMoney = int(curMoney) + int(msgDict['MONEY'])
            cgBool = self.db.updateData(self.user.myIdx, curMoney, 2)
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

        elif msgDict['MSG'] == '/RINF' or msgDict['MSG'] == '/CHWC':
            info = self.db.getRoomData(msgDict['RIDX'], 3)
            sendDict = self.mc.createItemDict(sendDict, info)
            sendDict['WATCH'] = self.db.checkWatch(self.user.myIdx, msgDict['RIDX'])
            if msgDict['MSG'] == '/CHWC':
                if sendDict['WATCH']:
                    self.db.updateWatch(msgDict['RIDX'], self.user.myIdx, 1)
                else:
                    self.db.updateWatch(msgDict['RIDX'], self.user.myIdx, 2)
                sendDict['WATCH'] = not sendDict['WATCH']
            sendDict['RIDX'] = msgDict['RIDX']

        elif msgDict['MSG'] == '/ACRQ':
            myIdx = self.user.myIdx
            preData = self.db.getRoomData(msgDict['RIDX'], 1)

            # itname, prebuyer, msg, sgDict
            self.sendAlarm(preData[0], preData[1], '/FAILED', msgDict['PRICE'], 0)

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

        elif msgDict['MSG'] == '/WCLT':
            wFlag = self.db.search(self.user.myIdx, 4)
            #wFlag가 없는지에 대한 True를 나타내므로 not wFlag로
            if not wFlag:
                sendDict['RPLY'] = 'ACK'
                sendDict['ROOMS'] = self.db.getMyRooms(self.user.myIdx, 3)
            sendDict['MSG'] = msgDict['MSG']
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
    def sendAlarm(self, buyer, itemName, msg, money, roomIdx):

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
            sendDict['RIDX'] = roomIdx

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
            print(img)
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
        myIdx = self.user.myIdx
        rooms = self.db.getMyRooms(myIdx, mode)
        sendDict['ROOMS'] = self.mc.createRoomList(rooms)
        return sendDict

    # send room list data to client
    def sendListRef(self, userList, mode):
        sendDict = {'MSG': '/RLST'}
        rooms = self.db.getMyRooms(self.mc.alarmIdx, 4)
        sendDict['ROOMS'] = self.mc.createRoomList(rooms)
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
        if len(self.threadList) == 0:
            self.server.destroy()