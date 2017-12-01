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
                aucData = self.db.getRoomData(self.room.roomIdx, 2)
                buyer = aucData[0]

                #money to buy item
                reqMoney = aucData[1]

                #get user's money
                money = self.db.getData_Index(buyer, 2)
                price = money - reqMoney
                if money >= reqMoney and buyer != None:
                    self.db.insert(self.room.roomIdx, 4)

                    # 구매자 돈 마이너스
                    self.db.updateData(buyer, price, 2)

                    # 판매자 돈 플러스
                    sellerIdx = self.db.getData(self.room.item.seller, 3)
                    self.db.updateData(sellerIdx, reqMoney + self.db.getData_Index(sellerIdx, 2), 2)

                    self.rcvThread.sendAlarm(buyer, self.room.item.itemName, '/SUCCESS', reqMoney, 0)
                    self.rcvThread.sendAlarm(sellerIdx, self.room.item.itemName, '/SELLER', reqMoney, self.room.roomIdx)
                else:
                    self.db.updateData(self.room.roomIdx, -1, 3)
                sendDict = {'RPLY': 'ACK', 'PRICE': reqMoney, 'RIDX': self.room.roomIdx}
                self.rcvThread.sendRoomRef(self.rcvThread.mc.userList, sendDict)
                break
            else:
                now = datetime.datetime.now()
                curTime = now.strftime('%Y-%m-%d %H:%M:%S')

