import zmq

partSize = 1024*1024*10

def sendIndexFile(socket, filename):
    with open(filename, "rb") as f:
        while True:
            data = f.read(partSize)
            request = socket.recv()
            if not data:
                break       
            socket.send_multipart([filename.encode("ascii"), data])
    socket.send_multipart([filename.encode("ascii"), b'done'])

def main():
    serversAddress = []
    usersTable = {}
    partsFilesTable = {}

    context = zmq.Context()
    serverSocket = context.socket(zmq.REP)
    serverSocket.bind("tcp://*:5555")

    clientSocket = context.socket(zmq.REP)
    clientSocket.bind("tcp://*:6666")

    poller = zmq.Poller()
    poller.register(serverSocket, zmq.POLLIN)
    poller.register(clientSocket, zmq.POLLIN)

    while True:
        sockets = dict(poller.poll())
        if clientSocket in sockets:
            operation, *args = clientSocket.recv_multipart()
            if operation == b'login':
                args[0].decode("ascii")
                if args[0] not in usersTable:
                    usersTable[args[0]] = {}
                    clientSocket.send('New User: {}'.format(args[0]).encode("ascii"))
                else:
                    clientSocket.send('Welcome Back: {}'.format(args[0]).encode("ascii"))

            if operation == b'availableServers':
                clientSocket.send_multipart(serversAddress)

            if operation == b'newFile':
                partsLocation = eval(args[3].decode("ascii"))
                user = args[2].decode("ascii")
                filename = args[1].decode("ascii")
                shaFile = args[0].decode("ascii")
                usersTable[user] = {filename : [shaFile, user]}
                partsFilesTable[shaFile] = partsLocation
                clientSocket.send("New File {}".format(filename).encode("ascii"))
            """ Download with index file
            if operation == b'download':
                user = args[0].decode("ascii")
                filename = args[1].decode("ascii")
                if user in usersTable.keys():
                    if filename in usersTable[user].keys():
                        clientSocket.send(b'yes')
                        sendIndexFile(clientSocket, usersTable[user][filename][0])       
                    else:
                        clientSocket.send(b'no')
                else:
                    clientSocket.send(b'no')
            """
            if operation == b'download':
                user = args[0].decode("ascii")
                filename = args[1].decode("ascii")
                if user in usersTable.keys():
                    if filename in usersTable[user].keys():
                        partsAndLocation = str(partsFilesTable[usersTable[user][filename][0]]).encode("ascii")
                        clientSocket.send(partsAndLocation)
                    else:
                        clientSocket.send(b'no')
                else:
                    clientSocket.send(b'no')

            if operation == b'share':
                user = args[0].decode("ascii")
                filename = args[1].decode("ascii")
                if filename in usersTable[user].keys():
                    clientSocket.send(b'yes')
                    toWho = clientSocket.recv()  
                    if toWho in usersTable.keys():
                        usersTable[toWho][filename] = usersTable[user][filename]
                        clientSocket.send(b'yes')
                    else:
                        clientSocket.send(b'no')   

                else:
                    clientSocket.send(b'no')

        if serverSocket in sockets:
            operation, *rest = serverSocket.recv_multipart()
            if operation == b'newServer':
                serversAddress.append(rest[0])
                serverSocket.send(b'Added')

if __name__ == '__main__':
    main()