import zmq, sys, hashlib

def recvIndexFile(socket, filename, data):
    socket.send(b'got')
    with open(filename, "wb") as f:
        while True:
            if data == b'done':
                break
            f.write(data)
            op, filename, data = socket.recv_multipart()
            socket.send(b'got')

#<---------CHORD---------->

def computeHash(bt):
    sha1 = hashlib.sha1()
    sha1.update(bt)
    return sha1.hexdigest()

class fingerTable(object):
    def __init__(self):
        self.table = []
        self.size = 160
        self.initTable()

    def initTable(self):
        for i in range(1, self.size):
            self.table.append(None)


class Node(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.id = computeHash(self.ip + ":" + self.port)
        self.successor = self
        self.predecessor = None
        self.fingerTable = fingerTable()
        self.next = 0

    def connect(self, socket):
        socket.send_multipart([b'newServer', bytes(self.id, "ascii")])
        response = socket.recv()
        print(response)
        if response != b'create':
            self.join(response.decode("ascii"))

    def join(self, newNode):
        self.successor = newNode.find_successor(self.id)
        
    def find_successor(self, id):
        if int(self.id, 16) < int(id, 16) and int(id, 16) <= int(self.successor, 16):
            return self.successor
        else:
            n0 = self.closest_preceding_node(id)
            return n0.find_successor()
    
    def closest_preceding_node(self, id):
        for i in range(self.fingerTable.size, 1):
            if int(self.id, 16) < self.finger(i) and self.finger(i) < int(id, 16):
                return self.finger(i)
        return self.id

    def finger(self, k):
        res = ( int(self.id, 16) + pow(2, k-1) ) % pow(2, self.fingerTable.size)
        return hex(res)[2:]

    def stabilize(self):
        x = self.successor.predecessor
        if int(self.id, 16) < int(x, 16) and int(x, 16) < int(self.successor, 16):
            self.successor = x
        self.successor.notify(self.id)

    def notify(self, node):
        if self.predecessor == None or ( int(self.predecessor, 16) < int(node, 16) and int(node, 16) < int(self.id, 16) ):
            self.predecessor = node

    def fix_fingers(self):
        self.next += 1
        if next > self.fingerTable.size:
            self.next = 1
        self.fingerTable.table[self.next] = self.find_successor(hex( int( self.id + pow(2, next-1) ) )[2:])

    def print(self):
        print("Nodo -> {} \n".format(self.id))
        print("--Successor -> {} -- Predecessor -> {}".format(self.successor, self.predecessor))
        print("----Finger Table --> \n")
        for i in range(0, self.fingerTable.size-1):
            print("------ {} -> {}".format(i, self.fingerTable.table[i]))

#Join or Create
node = Node(ip, port)
node.connect(proxySocket)
node.print()

#<!-------!CHORD---------!>

def main():
    if len(sys.argv) != 2:
        print("Sample call: python server.py <address: <ip>:<port>>")
        exit()

    filesFolder = "files/"

    clientAddress = sys.argv[1]
    print(clientAddress)
    context = zmq.Context()
    proxySocket = context.socket(zmq.REQ)
    proxySocket.connect("tcp://127.0.0.1:5555")

    clientSocket = context.socket(zmq.REP)
    clientSocket.bind("tcp://{}".format(clientAddress))

    proxySocket.send_multipart([b'newServer', bytes(clientAddress, "ascii")])
    response = proxySocket.recv()
    print(response)

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