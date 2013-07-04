import os
import sys
import socket
import SocketServer
import request
import sqlite3

import threading

config = {}

def recvupto(sock, c='\n'):
  data = ''
  while True:
    d = sock.recv(1)
    if d == '':
      return data
    data += d
    if d == c:
       return data
  return data


def handle(sock):
#  print("{} wrote:".format(self.client_address[0]))
  db_create = False
  if not os.path.isfile('db.sqlite'):
    db_create = True
  con = sqlite3.connect('db.sqlite')
  con.row_factory = sqlite3.Row

  if db_create:
    con.executescript(u'''
    PRAGMA foreign_keys=OFF;
    BEGIN TRANSACTION;
    CREATE TABLE configs (id integer primary key, localname varchar, origname varchar);
    CREATE TABLE stl (id integer primary key, localname varchar, origname varchar);
    CREATE TABLE stats (id integer primary key, cmd varchar, timestamp datetime not null, recvd integer default 0, sent integer default 0);
    COMMIT;
    ''')
    con.commit()

  #fd = sock.fileno()
  while True:
    cnt = recvupto(sock) #fd.readline()
    print cnt
    if cnt == '':
        break
    cnt = cnt.strip()
    print cnt

    print('request size:', cnt)
    data = sock.recv(int(cnt))
    #print(data)

    response = request.handle(data, con)

    sock.sendall(str(len(response))+'\n'+response)

import ssl
def do_main_program():
  bindsocket = socket.socket()
  bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  bindsocket.bind(('', 10000))
  bindsocket.listen(5)
  while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket,
      server_side=True,
      certfile="/home/mzatko/personal/deslicer/src/conf/cert/server.crt",
      keyfile="/home/mzatko/personal/deslicer/src/conf/cert/server.key",
      ssl_version=ssl.PROTOCOL_TLSv1)
    try:
      handle(connstream)
    finally:
      connstream.shutdown(socket.SHUT_RDWR)
      connstream.close()

def initial_program_setup():
  import ConfigParser

  config = ConfigParser.ConfigParser()
  config.read('penis.cfg')
  print ('SETUUUUUUUUUP!!!!!')

def program_cleanup():
  print ('CLEANUUUUUUUUP!!!')

def reload_program_config():
  print ('CONFIIIIIIIIIIG!!!!111')


