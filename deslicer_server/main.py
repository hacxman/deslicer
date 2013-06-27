import os
import sys
import socket
import SocketServer
import request
import sqlite3

import threading

#class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
#
#    def handle(self):
#        data = self.request.recv(1024)
#        cur_thread = threading.current_thread()
#        response = "{}: {}".format(cur_thread.name, data)
#        self.request.sendall(response)

class MyTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        print("{} wrote:".format(self.client_address[0]))
        con = sqlite3.connect('db.sqlite')
        con.row_factory = sqlite3.Row

        while True:
            cnt = self.rfile.readline()
            if cnt == '':
                break
            cnt = cnt.strip()

            print('request size:', cnt)
            data = self.rfile.read(int(cnt))
            #print(data)

            response = request.handle(data, con)

            self.wfile.write(str(len(response))+'\n'+response)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    address_family = socket.AF_INET6

def do_main_program():
    HOST, PORT = "", 9999

    server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
#    print server.server_address
    ip, port, _, _ = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print( "Server loop running in thread:", server_thread.name)

    server.serve_forever()
#    server.shutdown()




def initial_program_setup():
  print ('SETUUUUUUUUUP!!!!!')

#class TCPServer(SocketServer.TCPServer):
#    allow_reuse_address = True
#    address_family = socket.AF_INET6
#
#def do_main_program():
#    HOST, PORT = "::1", 9999
#
#    # Create the server, binding to localhost on port 9999
#    server = TCPServer((HOST, PORT), MyTCPHandler)
#
#    # Activate the server; this will keep running until you
#    # interrupt the program with Ctrl-C
#    server.serve_forever()

def program_cleanup():
  print ('CLEANUUUUUUUUP!!!')

def reload_program_config():
  print ('CONFIIIIIIIIIIG!!!!111')


