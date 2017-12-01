
from Controller import Server
import socket
def main():
    sFlag = True
    host = ''
    port = 8099
    index = 1
    serverList = {}
    clientList = []
    clientMax = 2

    # wait for another client
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(10)

    # Load Balancer for Server
    while True:
        clientSocket, addr = serverSocket.accept()
        for i in range(len(serverList)):

            if len(serverList[i+1].threadList) < clientMax:
                sFlag = False
                index = i+1
                break
            elif i == len(serverList)-1 and len(serverList[i+1].threadList) >= clientMax:
                sFlag = True
                index = len(serverList) +1
                break
            index = int(i)

        if sFlag:
            server = Server.Server(index+port, clientList)
            print('Create New Server')
            server.start()
            serverList[index] = server

        msg = str(port+index)
        msg = msg.encode("utf-8")
        clientSocket.send(msg)
        index = 1
        sFlag = False
        clientSocket.close()

    print("End Server")

if __name__ == "__main__":
    main()