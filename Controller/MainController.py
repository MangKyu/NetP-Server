from Model import Item, Room
from Controller import RoomThread

class MainController:
    roomList = None
    roomThreadList = None
    userList = None
    alarmIdx = 0
    threadList = None

    # Constructor for Main Controller instance
    def __init__(self, userList, threadList):
        self.threadList = threadList
        self.alarmIdx = 0
        self.roomList = {}
        self.roomThreadList = []
        self.userList = userList

    # create item instance
    def createItem(self, msgDict, roomIdx):
        imgPath = str(roomIdx) + '_' + msgDict['SELLER'] + '_' + msgDict['ITNAME']+'.' + msgDict['ITPATH']
        item = Item.Item(msgDict['SELLER'], msgDict['ITNAME'], msgDict['PRICE'], msgDict['ITDESC'], imgPath, None)
        return item

    # create item dictionary instance
    def createItemDict(self, sendDict, info):
        sendDict['MSG'] = '/RINF'
        sendDict['RPLY'] = 'ACK'
        sendDict['ENDT'] = str(info[0])
        sendDict['SELLER'] = info[1]
        sendDict['PRICE'] = info[2]
        sendDict['ITNAME'] = info[3]
        sendDict['ITPATH'] = info[4]
        sendDict['ITDESC'] = info[5]
        return sendDict

    # create room for item
    def createRoom(self, roomIdx, endTime, item):
        self.roomList[roomIdx] = Room.Room(roomIdx, endTime, item)

    # create room thread
    def createRoomThread(self, rcvThread, roomIdx, db):
        roomThread = RoomThread.RoomThread(rcvThread, self.roomList[roomIdx], self.alarmIdx, db)
        self.roomThreadList.append(roomThread)
        roomThread.start()

    # create room list
    def createRoomList(self, rooms):
        roomList = []
        for i in range(len(rooms)):
            roomList.append(rooms[i])
        return roomList
