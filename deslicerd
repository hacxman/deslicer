#!/usr/bin/python
import os
import sys
import socket
import SocketServer
import request
import sqlite3

class MyTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        print "{} wrote:".format(self.client_address[0])
        con = sqlite3.connect('db.sqlite')
        con.row_factory = sqlite3.Row

        while True:
            cnt = self.rfile.readline()
            if cnt == '':
                break
            cnt = cnt.strip()

            print cnt
            data = self.rfile.read(int(cnt))
            print data

            response = request.handle(data, con)

            self.wfile.write(str(len(response))+'\n'+response)

def initial_program_setup():
  print 'SETUUUUUUUUUP!!!!!'

class TCPServer(SocketServer.TCPServer):
    allow_reuse_address = True
    address_family = socket.AF_INET6

def do_main_program():
    HOST, PORT = "::1", 9999

    # Create the server, binding to localhost on port 9999
    server = TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

def program_cleanup():
  print 'CLEANUUUUUUUUP!!!'

def reload_program_config():
  print 'CONFIIIIIIIIIIG!!!!111'

if __name__=='__main__':
  if '-d' in sys.argv:
    import deamon
  else:
    try:
      initial_program_setup()
      reload_program_config()
      do_main_program()
    except Exception as e:
      print e
      program_cleanup()
      raise e

