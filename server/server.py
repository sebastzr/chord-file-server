import zmq, sys

if len(sys.argv) != 2:
    print("Sample call: python <server.py> <address: <ip>:<port>>")
    exit()
clientAddress = sys.argv[1]

context = zmq.Context()
proxySocket = context.socket(zmq.REP)
proxySocket.bind("tcp://localhost:5555")

clientSocket = context.socket(zmq.REP)
clientSocket.bind("tcp://{}".format(clientAddress))

proxySocket.send_multipart([b'newServer',bytes(clientAddress, "ascii")])
response = proxySocket.recv()
print(response)

while True:
    filename, data = proxySocket.recv_multipart()
    with open(filename, "ab") as f:
        f.write(data)
    proxySocket.send(b"Done")