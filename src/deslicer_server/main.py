import os
import sys
import socket
import SocketServer
import request
import sqlite3

import threading

##class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
##
##    def handle(self):
##        data = self.request.recv(1024)
##        cur_thread = threading.current_thread()
##        response = "{}: {}".format(cur_thread.name, data)
##        self.request.sendall(response)
#
#class MyTCPHandler(SocketServer.StreamRequestHandler):
#
#    def handle(self):
#        print("{} wrote:".format(self.client_address[0]))
#        con = sqlite3.connect('db.sqlite')
#        con.row_factory = sqlite3.Row
#
#        while True:
#            cnt = self.rfile.readline()
#            if cnt == '':
#                break
#            cnt = cnt.strip()
#
#            print('request size:', cnt)
#            data = self.rfile.read(int(cnt))
#            #print(data)
#
#            response = request.handle(data, con)
#
#            self.wfile.write(str(len(response))+'\n'+response)
#
#
#class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
#    allow_reuse_address = True
#    address_family = socket.AF_INET6
#
##from OpenSSL import SSL
#import ssl
#import socket, SocketServer
#
#class SSLSocketServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
#
#    allow_reuse_address = True
#    address_family = socket.AF_INET6
#
#    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
#        SocketServer.BaseServer.__init__(self, server_address,
#            RequestHandlerClass)
#        ctx = SSL.Context(SSL.TLSv1_METHOD)
#        #cert = '../conf/cert/server.crt'
#        #key = '../conf/cert/server.key'
#        #ctx.use_privatekey_file(key)
#        #ctx.use_certificate_file(cert)
#        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
#            self.socket_type))
#        if bind_and_activate:
#            self.server_bind()
#            self.server_activate()
#    def shutdown_request(self,request):
#        request.shutdown()
#
#
#def _do_main_program():
#    HOST, PORT = "", 10000
#
#    #server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
#    server = SSLSocketServer((HOST, PORT), MyTCPHandler)
##    print server.server_address
#    ip, port, _, _ = server.server_address
#
#    # Start a thread with the server -- that thread will then start one
#    # more thread for each request
#    server_thread = threading.Thread(target=server.serve_forever)
#    # Exit the server thread when the main thread terminates
#    server_thread.daemon = True
#    server_thread.start()
#    print( "Server loop running in thread:", server_thread.name)
#
#    server.serve_forever()
##    server.shutdown()
#

def recvupto(sock, c='\n'):
  data = ''
  while True:
    d = sock.recv(1)
    data += d
    if d == c:
       return data
  return data


def handle(sock):
#    print("{} wrote:".format(self.client_address[0]))
    con = sqlite3.connect('db.sqlite')
    con.row_factory = sqlite3.Row

    #fd = sock.fileno()
    while True:
        cnt = recvupto(sock) #fd.readline()
        if cnt == '':
            break
        cnt = cnt.strip()

        print('request size:', cnt)
        data = sock.recv(int(cnt))
        #print(data)

        response = request.handle(data, con)

        sock.sendall(str(len(response))+'\n'+response)

from eventlet.green import socket
from eventlet.green.OpenSSL import SSL

def do_main_program():
  # insecure context, only for example purposes
  context = SSL.Context(SSL.SSLv23_METHOD)
  context.set_verify(SSL.VERIFY_NONE, lambda *x: True)

  # create underlying green socket and wrap it in ssl
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  connection = SSL.Connection(context, sock)

  # configure as server
  connection.set_accept_state()
  connection.bind(('127.0.0.1', 10000))
  connection.listen(50)

  pool = eventlet.GreenPool(10000)
  while True:
    try:
      client_conn, addr = connection.accept()
      try:
        print "accepted", address
        pool.spawn_n(handle, client_conn)
      finally:
        print 'wat'
        client_conn.shutdown()
        client_conn.close()
        #connstream.shutdown(socket.SHUT_RDWR)
        #connstream.close()

    except (SystemExit, KeyboardInterrupt):
      break

  connection.close()


#import eventlet
#from eventlet.green import  ssl
#
#def do_main_program():
#  server = eventlet.listen(('', 10000))
#  pool = eventlet.GreenPool(10000)
#  while True:
#    try:
#      new_sock, address = server.accept()
#      connstream = ssl.wrap_socket(new_sock,
#                                 server_side=True,
#                                 certfile="/home/hacxman/src/deslic3r/d/deslicer/conf/cert/server.crt",
#                                 keyfile="/home/hacxman/src/deslic3r/d/deslicer/conf/cert/server.key",
#                                 ssl_version=ssl.PROTOCOL_TLSv1)
#
#      try:
#        print "accepted", address
#        pool.spawn_n(handle, connstream)
##       deal_with_client(connstream)
#      finally:
#        print 'wat'
#        connstream.shutdown(socket.SHUT_RDWR)
#        connstream.close()
#
#    except (SystemExit, KeyboardInterrupt):
#      break

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


