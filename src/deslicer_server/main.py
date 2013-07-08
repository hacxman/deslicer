import os
import sys
import socket
import SocketServer
import request
import sqlite3

import threading

import logging
logging.basicConfig(filename='/var/log/deslicer.log',level=logging.DEBUG)

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
    CREATE TABLE journal (id integer primary key, cmd varchar, pid integer, timestamp datetime not null, action varchar, status integer);
    COMMIT;
    ''')
    con.commit()

  #fd = sock.fileno()
  while True:
    cnt = recvupto(sock) #fd.readline()
    logging.info( cnt)
    if cnt == '':
        break
    cnt = cnt.strip()
    logging.info( cnt)

    logging.info(('request size:', cnt))
    data = ''
    datalen = 0
    while datalen != int(cnt):
      d = sock.recv(int(cnt)-datalen)
      if d == '':
        break
      data += d
      datalen += len(d)
    #logging.info((data))

    response = request.handle(data, con, apikey=config['apikey'])

    sock.sendall(str(len(response))+'\n'+response)

import ssl
import traceback
def _ssl_handle(newsocket, fromaddr):
  try:
    connstream = ssl.wrap_socket(newsocket,
      server_side=True,
      certfile="/etc/pki/tls/deslicer/server.crt",
      keyfile="/etc/pki/tls/deslicer/server.key",
      ssl_version=ssl.PROTOCOL_TLSv1)
    handle(connstream)
  except Exception as e:
    logging.error( traceback.format_exc())
  finally:
    try:
      connstream.shutdown(socket.SHUT_RDWR)
    except socket.error as e:
      logging.error( traceback.format_exc())
    connstream.close()

def do_main_program():
  bindsocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  bindsocket.bind(('', 9999))
  bindsocket.listen(5)
  while True:
    newsocket, fromaddr = bindsocket.accept()
    th = threading.Thread(target=_ssl_handle, args=(newsocket, fromaddr))
    th.start()

def initial_program_setup():
  import ConfigParser
  _config = ConfigParser.ConfigParser()
  if len(_config.read(os.path.expanduser('/etc/deslicer.conf'))) == 0:
    logging.info( 'cannot parse /etc/deslicer.conf')
    exit(1)
  config['apikey'] = _config.get('server', 'apikey').strip()
  logging.info('apikey = '+config['apikey'])

  logging.info( 'SETUUUUUUUUUP!!!!!')

def program_cleanup():
  logging.info( 'CLEANUUUUUUUUP!!!')

def reload_program_config():
  logging.info( 'CONFIIIIIIIIIIG!!!!111')


