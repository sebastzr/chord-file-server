#<---------CHORD---------->
import hashlib


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
        self.id = ""
        self.successor = self
        self.predecessor = None
        self.fingerTable = fingerTable()
        self.next = 0
        self.socket = ''

    def computeHash(self, bt):
        sha1 = hashlib.sha1()
        sha1.update(bytes(bt, "ascii"))
        return sha1.hexdigest()

    def set_hash(self):
        self.id = self.computeHash(self.ip + ":" + self.port)

    def set_socket(self, socket):
        self.socket = socket

    def connect(self):
        self.socket.send_multipart([ b'newServer', bytes(self.ip, "ascii"), bytes(self.port, "ascii") ])
        response, *rest = self.socket.recv_multipart()
        print(response)
        self.id = rest[0]
        if response != b'create':
            newNode = Node(rest[2].decode('ascii'), rest[3].decode('ascii'))
            newNode.id = rest[1].decode('ascii')
            self.join(newNode)
            
    def join(self, newNode):
        self.successor = newNode.find_successor(self.id)
        
    def find_successor(self, id):
        if int(self.id, 16) < int(id, 16) and int(id, 16) <= int(self.successor.id, 16):
            return self.successor
        else:
            n0 = self.closest_preceding_node(id)
            return n0.find_successor(id)
    
    def closest_preceding_node(self, id):
        for i in range(self.fingerTable.size, 1):
            if int(self.id, 16) < self.finger(i) and self.finger(i) < int(id, 16):
                self.socket.send_multipart([b'who', self.finger(i)])
                res, *rest = self.socket.recv_multipart()
                return Node(rest[0], rest[1])
        return self

    def finger(self, k):
        res = ( int(self.id, 16) + pow(2, k-1) ) % pow(2, self.fingerTable.size)
        return hex(res)[2:]

    def stabilize(self):
        x = self.successor.predecessor
        if int(self.id, 16) < int(x, 16) and int(x, 16) < int(self.successor.id, 16):
            self.successor = x
        self.successor.notify(self)

    def notify(self, node):
        if self.predecessor == None or ( int(self.predecessor.id, 16) < int(node, 16) and int(node, 16) < int(self.id, 16) ):
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
            if self.fingerTable.table[i] != None:
                print("------ {} -> {}".format(i, self.fingerTable.table[i]))