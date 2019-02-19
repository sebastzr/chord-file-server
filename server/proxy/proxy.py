import zmq

def main():
    serversAddress = []
    context = zmq.Context()

    serverSocket = context.socket(zmq.REP)
    serverSocket.bind("tcp://*:5555)

    clientSocket = context.socket(zmq.REP)
    clientSocket.bind("tcp://*:6666)

    poller = zmq.Poller()
    poller.register(serverSocket, zmq.POLLIN)
    poller.register(clientSocket, zmq.POLLIN)

    while True:
        sockets = dict(poller.poll())
        if clientSocket in sockets:
            operation, *args = clientSocket.recv_multipart()
            if operation == b'upload':
                clientSocket.send(serversAddress)

        if serverSocket in sockets:
            operation, *rest = serverSocket.recv_multipart()
            if operation == b'newServer':
                serversAddress.append(rest[0])
                serverSocket.send(b'Added')