from Controller import RCVThread, DBConnection
import socket
from Controller import MainController
import threading
class Server(threading.Thread):
    port = 8099
    host = ''
    userList = []
    threadList = None
    serverSocket = None
    clientList = None
    db = None
    mc = None

    # Constructor for Server Instrance
    def __init__(self, port, clientList):
        threading.Thread.__init__(self)
        self.port = port
        self.clientList = clientList
        self.mc = MainController.MainController(self.userList, self.threadList)
        self.db = DBConnection.DBConnection()
        self.threadList = []

    # kill every thread and close client socket
    def killClient(self):
        for i in self.threadList:
            self.threadList[i].exit()
            self.userList[i].clientSock.close()

    # wait for another client
    def run(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.host, self.port))
        self.serverSocket.listen(10)

        while True:
            clientSocket, addr = self.serverSocket.accept()
            rcvThread = RCVThread.RCVThread(self, self.threadList, clientSocket, self.db, self.mc)
            self.threadList.append(rcvThread)
            self.clientList.append(clientSocket)
            rcvThread.start()
        self.killClient()
        self.db.exitDB()