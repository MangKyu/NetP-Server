import pymysql
import datetime

# class for connection to DataBase
class DBConnection:
    conn = None
    curs = None

    def __init__(self):
        # Connect to database
        self.conn = pymysql.connect(host='localhost', user='root', password='apmsetup',
                                    db='konkuk', charset='utf8')

        # From conn, make Dictionary Cursor
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)

    # insert the tuple to db
    def insert(self, msgDict, mode):
        try:
            with self.conn.cursor() as cursor:
                # insert user data into user table
                if mode == 1:
                    sql = 'INSERT INTO user (name, id, pw, mail) VALUES (%s, %s, %s, %s)'
                    cursor.execute(sql, (msgDict['NAME'], msgDict['ID'], msgDict['PW'], msgDict['MAIL']))

                # insert into room data into room table
                elif mode == 2:
                    sql = 'INSERT INTO room (startTime, endTime, price) VALUES (%s, %s, %s)'
                    nowDateTime, laterDateTime = self.createDate()
                    cursor.execute(sql, (nowDateTime, laterDateTime, msgDict['PRICE']))
                    roomIdx = self.getData(None, 5)
                    return True, roomIdx, laterDateTime

                # insert item data into item table
                elif mode == 3:
                    item = msgDict['ITEM']
                    roomIdx = self.getData(item.seller, 5)
                    seller = self.getData(item.seller, 1)
                    sql = 'INSERT INTO item (roomIdx, seller, itemName, imgPath, itemDesc) ' \
                          'VALUES (%s, %s, %s, %s, %s) '
                    cursor.execute(sql, (int(roomIdx), int(seller), item.itemName,
                                         item.imgPath, item.itemDesc))
                self.conn.commit()
                return True
        finally:
            pass

    # update the data to database
    def updateData(self, id, data, mode):
        try:
            with self.conn.cursor() as cursor:
                # change password in use rta
                if mode == 1:
                    sql = 'UPDATE user SET pw = %s WHERE id = %s'

                # update current money in user table
                elif mode == 2:
                    sql = 'UPDATE user SET money = %s WHERE id = %s'
                    data = int(data)

                # update auction price in room table
                elif mode == 3:
                    sql = 'UPDATE room SET price = %s WHERE roomIdx = %s'
                    id = int(id)
                    data = int(data)

                cursor.execute(sql, (data, id))
                self.conn.commit()
                return True
        finally:
            pass

    def getMyRooms(self, myIdx, mode):
        try:
            now = datetime.datetime.now()
            nowDateTime = now.strftime('%Y-%m-%d %H:%M:%S')
            with self.conn.cursor() as cursor:
                if mode == 1:
                    sql = 'SELECT item.roomIdx, user.name,itemName FROM item, user,room where item.roomIdx = room.roomIdx' \
                          ' and user.myIdx = room.prebuyer and room.prebuyer = %s and room.endTime > %s and room.startTime <= %s'
                    cursor.execute(sql, (int(myIdx), nowDateTime, nowDateTime))
                elif mode == 2:
                    sql = 'SELECT item.roomIdx, user.name,itemName FROM item, user, auclist where auclist.teller = %s and auclist.teller = user.myIdx and auclist.roomIdx = item.roomIdx'
                    cursor.execute(sql, int(myIdx))
                result = cursor.fetchall()
                self.conn.commit()
                return result
        finally:
            pass

    def getRooms(self, alarmIdx):
        try:
            with self.conn.cursor() as cursor:
                sql = 'SELECT item.roomIdx, user.name,itemName FROM item, user where item.seller = user.myIdx and item.roomIdx > %s'
                cursor.execute(sql, int(alarmIdx))
                result = cursor.fetchall()
                self.conn.commit()
                return result
        finally:
            pass

    def getAucData(self, roomIdx):
        try:
            with self.conn.cursor() as cursor:
                sql = 'SELECT prebuyer, price FROM room where room.roomIdx = %s'
                cursor.execute(sql, int(roomIdx))
                result = cursor.fetchone()
                self.conn.commit()
                return result
        finally:
            pass

    # delete the tuple from db
    def delete(self, id):
        try:
            with self.conn.cursor() as cursor:
                sql = 'DELETE FROM user WHERE id = %s'
                cursor.execute(sql, id)
                self.conn.commit()
        finally:
            pass

    # search the tuple from db
    def search(self, msg, mode):
        try:
            with self.conn.cursor() as cursor:
                # search ID
                if mode == 1:
                    sql = 'SELECT id FROM user WHERE id = %s '

                # search PW
                elif mode == 2:
                    sql = 'SELECT pw FROM user WHERE pw = %s '

                # search Mail
                elif mode == 3:
                    sql = 'SELECT mail FROM user WHERE mail = %s '

                cursor.execute(sql, msg)
                result = cursor.fetchone()
                self.conn.commit()
                if not result:
                    return True
                else:
                    return False
        finally:
            pass

    # search the tuple from db
    def getData(self, data, mode):
        try:
            with self.conn.cursor() as cursor:
                # get myIdx
                if mode == 1:
                    sql = 'SELECT myIdx FROM user WHERE id = %s'

                # get name
                elif mode == 2:
                    sql = 'SELECT name FROM user WHERE id = %s '

                # get money
                elif mode == 3:
                    sql = 'SELECT money FROM user WHERE id = %s '

                # get pw
                elif mode == 4:
                    sql = 'SELECT pw FROM user WHERE id = %s '

                # get roomIdx
                elif mode == 5:
                    sql = 'SELECT roomIdx FROM room ORDER BY roomIdx DESC LIMIT 1'

                elif mode == 6:
                    sql = 'SELECT prebuyer FROM room WHERE roomIdx = %s'
                    data = int(data)

                if mode == 5:
                    cursor.execute(sql, None)
                else:
                    cursor.execute(sql, data)
                result = cursor.fetchone()
                self.conn.commit()
                return result[0]
        finally:
            pass

    def getPreBuyer(self, roomIdx):
        try:
            with self.conn.cursor() as cursor:
                sql = 'select item.itemName, room.prebuyer from item, room where room.roomIdx = item.roomIdx and room.roomIdx = %s'
                cursor.execute(sql, roomIdx)
                self.conn.commit()
                result = cursor.fetchone()
                return result
        finally:
            pass

    def reqAuction(self, roomIdx, myIdx, price):
        try:
            with self.conn.cursor() as cursor:
                sql = 'update room set prebuyer = %s, price = %s where roomIdx = %s'
                cursor.execute(sql, (int(myIdx), int(price), int(roomIdx)))
                self.conn.commit()
                return True
        finally:
            pass

    def insertAuc(self, roomIdx):
        teller = self.getData(roomIdx, 6)
        try:
            with self.conn.cursor() as cursor:
                sql = 'INSERT INTO auclist (roomIdx, teller) VALUES (%s, %s)'
                cursor.execute(sql, (int(roomIdx), int(teller)))
                self.conn.commit()
                return True
        finally:
            pass

    def getItem(self, roomIdx):
        try:
            with self.conn.cursor() as cursor:
                sql = 'SELECT room.endTime, user.id, room.price,item.itemName, item.imgPath, item.itemDesc FROM item, ' \
                      'user, room where item.seller = user.myIdx and room.roomIdx = item.roomIdx and room.roomIdx = %s'
                cursor.execute(sql, int(roomIdx))
                result = cursor.fetchone()
                self.conn.commit()
                return result
        finally:
            pass

    # create date for room
    def createDate(self):
        now = datetime.datetime.now()
        nowDateTime = now.strftime('%Y-%m-%d %H:%M:%S')
        later = (datetime.datetime.now() + datetime.timedelta(minutes=1))
        laterDateTime = later.strftime('%Y-%m-%d %H:%M:%S')
        return nowDateTime, laterDateTime

    # close db
    def exitDB(self):
        self.conn.close()
