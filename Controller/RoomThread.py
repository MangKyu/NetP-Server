import threading
import datetime
class RoomThread(threading.Thread):
    room = None
    rcvThread = None
    db = None

    # Constructor for Room Thread
    def __init__(self, rcvThread, room, alarmIdx, db):
        self.db = db
        self.alarmIdx = alarmIdx
        threading.Thread.__init__(self)
        self.room = room
        self.rcvThread = rcvThread

    # Count time for auction time
    def run(self):
        now = datetime.datetime.now()
        curTime = now.strftime('%Y-%m-%d %H:%M:%S')
        endTime = self.room.endTime
        while True:
            if curTime >= endTime:
                self.alarmIdx = self.room.roomIdx
                aucData = self.db.getAucData(self.room.roomIdx)
                buyer = aucData[0]

                #money to buy item
                reqMoney = aucData[1]
                #get user's money
                money = self.db.getData(self.rcvThread.user.id, 3)
                price = money - reqMoney
                if money >= reqMoney and buyer != None:
                    msg = '/SUCCESS'
                    self.db.insertAuc(self.room.roomIdx)
                    self.db.updateData(self.rcvThread.user.id, price, 2)
                    self.rcvThread.sendAlarm(buyer, self.room.item.itemName, msg, price)
                else:
                    self.db.updateData(self.room.roomIdx, -1, 3)
                sendDict = {'RPLY': 'ACK', 'PRICE': price, 'RIDX': self.room.roomIdx}
                self.rcvThread.sendRoomRef(self.rcvThread.mc.userList, sendDict)
                break
            else:
                now = datetime.datetime.now()
                curTime = now.strftime('%Y-%m-%d %H:%M:%S')

