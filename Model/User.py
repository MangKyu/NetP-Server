

class User:
    id = None
    money = None
    clientSock = None
    myIdx = None

    # constructor for user instance
    def __init__(self, clientSock, id, money, myIdx):
        self.clientSock = clientSock
        self.id = id
        self.money = money
        self.myIdx = myIdx