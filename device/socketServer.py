import socket, threading
import sys, subprocess

class BaseServer():

    def __init__(self, EventHandler):
        self.EventHandler = EventHandler

    # handle one connection, execute queue on recv data. Close connection
    def socketHandler(self, sock, addr):
        print("Entered handler", addr[0])
        data = sock.recv(1024)
        if data:
            print(data)
            self.EventHandler.init(data)
        sock.close()
        print("Handler closed", addr[0])

    # handles one connection at a time to avoid runtime issues with threads.
    def socketServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Bounded")
        s.bind(('', 8000))
        print("listening")
        s.listen(1)

        while True:
            print("waiting...")
            sock, addr = s.accept()
            print("connection made")
            threading.Thread(target=self.socketHandler, args=(sock, addr)).start()

        s.close()
