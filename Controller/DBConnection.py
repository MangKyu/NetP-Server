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
    def insert(self, data, mode):
        try:
            with self.conn.cursor() as cursor:
                # insert user data into user table
                if mode == 1:
                    sql = 'INSERT INTO user (name, id, pw, mail) VALUES (%s, %s, %s, %s)'
                    cursor.execute(sql, (data['NAME'], data['ID'], data['PW'], data['MAIL']))

                # insert into room data into room table
                elif mode == 2:
                    sql = 'INSERT INTO room (startTime, endTime, price) VALUES (%s, %s, %s)'
                    nowDateTime, laterDateTime = self.createDate()
                    cursor.execute(sql, (nowDateTime, laterDateTime, data['PRICE']))
                    roomIdx = self.getData(None, 1)
                    return True, roomIdx, laterDateTime

                # insert item data into item table
                elif mode == 3:
                    item = data['ITEM']
                    roomIdx = self.getData(None, 1)
                    seller = self.getData(item.seller, 3)
                    sql = 'INSERT INTO item (roomIdx, seller, itemName, imgPath, itemDesc) ' \
                          'VALUES (%s, %s, %s, %s, %s) '
                    cursor.execute(sql, (int(roomIdx), int(seller), item.itemName,
                                         item.imgPath, item.itemDesc))
                #insert auction
                elif mode == 4:
                    teller = self.getData(data, 2)
                    sql = 'INSERT INTO auclist (roomIdx, teller) VALUES (%s, %s)'
                    cursor.execute(sql, (int(data), int(teller)))
                self.conn.commit()
                return True
        finally:
            pass

        # update the data to database
    def updateData(self, index, data, mode):
        try:
            with self.conn.cursor() as cursor:
                # change password in use rta
                if mode == 1:
                    sql = 'UPDATE user SET pw = %s WHERE myIdx = %s'

                # update current money in user table
                elif mode == 2:
                    sql = 'UPDATE user SET money = %s WHERE myIdx = %s'
                    data = int(data)
                # update auction price in room table
                elif mode == 3:
                    sql = 'UPDATE room SET price = %s WHERE roomIdx = %s'
                    data = int(data)
                cursor.execute(sql, (data, index))
                self.conn.commit()
                return True
        finally:
            pass

    def getMyRooms(self, index, mode):
        try:
            now = datetime.datetime.now()
            nowDateTime = now.strftime('%Y-%m-%d %H:%M:%S')
            with self.conn.cursor() as cursor:
                if mode == 1:
                    sql = 'SELECT item.roomIdx, user.name,itemName FROM item, user,room where item.roomIdx = room.roomIdx' \
                          ' and user.myIdx = room.prebuyer and room.prebuyer = %s and room.endTime > %s and room.startTime <= %s'
                    cursor.execute(sql, (int(index), nowDateTime, nowDateTime))
                elif mode == 2:
                    sql = 'SELECT item.roomIdx, user.name,itemName FROM item, user, auclist where auclist.teller = %s and auclist.teller = user.myIdx and auclist.roomIdx = item.roomIdx'
                elif mode == 3:
                    sql = 'select itemName, imgPath, price, room.roomIdx FROM room, item, watchlist where watchlist.roomIdx=room.roomIdx ' \
                          'and room.roomIdx = item.roomIdx and watchlist.myIdx = %s'
                elif mode == 4:
                    sql = 'SELECT item.roomIdx, user.name,itemName FROM item, user where item.seller = user.myIdx and item.roomIdx > %s'
                if mode != 1:
                    cursor.execute(sql, int(index))
                result = cursor.fetchall()
                self.conn.commit()
                return result
        finally:
            pass

    # delete the tuple from db
    def updateWatch(self, roomIdx, myIdx, mode):
        try:
            with self.conn.cursor() as cursor:
                if mode == 1:
                    sql = 'DELETE FROM watchlist WHERE myIdx = %s and roomIdx = %s'
                elif mode == 2:
                    sql = 'INSERT INTO watchlist (myIdx, roomIdx) VALUES (%s, %s)'
                cursor.execute(sql, (myIdx, roomIdx))
                self.conn.commit()
                return True
        finally:
            return False

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
                elif mode == 4:
                    sql = 'SELECT roomIdx FROM watchlist WHERE myIdx = %s'
                    msg = int(msg)

                cursor.execute(sql, msg)
                result = cursor.fetchone()
                self.conn.commit()
                if not result:
                    return True
                else:
                    return False
        finally:
            pass

    def checkWatch(self, myIdx, roomIdx):
        try:
            with self.conn.cursor() as cursor:
                # check watchlist
                sql = 'SELECT roomIdx FROM watchlist WHERE myIdx = %s and roomIdx = %s'
                cursor.execute(sql, (myIdx, roomIdx))
                result = cursor.fetchone()
                self.conn.commit()
                if result:
                    return True
                else:
                    return False
        finally:
            pass

    def getData_Index(self, data, mode):
        try:
            with self.conn.cursor() as cursor:
                # get password
                if mode == 1:
                    sql = 'SELECT pw FROM user WHERE myIdx = %s '

                # get Money
                elif mode == 2:
                    sql = 'SELECT money FROM user WHERE myIdx = %s '
                    data = int(data)
                # get name
                elif mode == 3:
                    sql = 'SELECT name FROM user WHERE myIdx = %s '

                cursor.execute(sql, data)
                result = cursor.fetchone()
                self.conn.commit()
                return result[0]
        finally:
            pass

    def getRoomData(self, roomIdx, mode):
        try:
            with self.conn.cursor() as cursor:
                if mode == 1:
                    sql = 'select room.prebuyer, item.itemName from item, room where room.roomIdx = item.roomIdx and room.roomIdx = %s'
                elif mode == 2:
                    sql = 'SELECT prebuyer, price FROM room where room.roomIdx = %s'
                elif mode == 3:
                    sql = 'SELECT room.endTime, user.id, room.price,item.itemName, item.imgPath, item.itemDesc FROM item, ' \
                          'user, room where item.seller = user.myIdx and room.roomIdx = item.roomIdx and room.roomIdx = %s'
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

    def getData(self, data, mode):
        try:
            with self.conn.cursor() as cursor:
                # get myIdx
                if mode == 1:
                    sql = 'SELECT roomIdx FROM room ORDER BY roomIdx DESC LIMIT 1'

                # get name
                elif mode == 2:
                    sql = 'SELECT prebuyer FROM room WHERE roomIdx = %s'
                    data = int(data)
                elif mode == 3:
                    sql = 'SELECT myIdx FROM user WHERE id = %s'
                if mode == 1:
                    cursor.execute(sql, None)
                else:
                    cursor.execute(sql, data)
                result = cursor.fetchone()
                self.conn.commit()
                return result[0]
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
