import zmq, sys
from node import Node

def recvIndexFile(socket, filename, data):
    socket.send(b'got')
    with open(filename, "wb") as f:
        while True:
            if data == b'done':
                break
            f.write(data)
            op, filename, data = socket.recv_multipart()
            socket.send(b'got')

def main():
    if len(sys.argv) != 3:
        print("Sample call: python server.py <ip> <port>")
        exit()

    filesFolder = "files/"

    ip = sys.argv[1]
    port = sys.argv[2]
    clientAddress = ip + ":" + port
    print(clientAddress)
    context = zmq.Context()
    proxySocket = context.socket(zmq.REQ)
    proxySocket.connect("tcp://127.0.0.1:5555")

    clientSocket = context.socket(zmq.REP)
    clientSocket.bind("tcp://{}".format(clientAddress))

    #Join or Create
    node = Node(ip, port)
    node.set_socket(proxySocket)
    node.connect()
    node.print()

    while True:
        operation, *data = clientSocket.recv_multipart()
        if operation == b'upload':
            filename, bt, sha1bt, sha1File = data
            storeAs = filesFolder + sha1bt.decode("ascii")
            with open(storeAs, "wb") as f:
                f.write(bt)
            clientSocket.send(b"Done")
        elif operation == b'download':
            f = open(filesFolder+data[0].decode("ascii"), "rb")
            partOfFile = f.read()
            clientSocket.send(partOfFile)
        elif operation == b'uploadIndexFile':
            recvIndexFile(clientSocket, data[0].decode("ascii"), data[1])
        else:
            clientSocket.send(b'Unsupported operation')
        

if __name__ == '__main__':
    main()