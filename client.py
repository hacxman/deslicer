#!/usr/bin/python
import json
import socket
import sys
import base64
import os

def readupto(fd, c='\n'):
  data = ''
  while True:
    d = os.read(fd, 1)
    data += d
    if d == c:
       return data
  return data


def talkto(data, sock):
    data = json.dumps(data)
    sock.sendall(str(len(data))+"\n"+data)

    # Receive data from the server and shut down
    fd = sock.fileno()
    n = int(readupto(fd).strip())
    cnt = 0
    res = ''
    while cnt != n:
      sz = 4096 if cnt < n - 4096 else n - cnt
      r = os.read(fd, sz)
      cnt += sz
      res += r
    return json.loads(res)

def show_help():
  print """usage: deslicer_client.py COMMAND [PARAM]
COMMANDS are one of:
  import STLFILE            - import an STL file
  importconfig CFGFILE      - import slic3r ini file
  ping                      - ping server
  listi                     - list imported STLs
  listc                     - list imported configs
  listd                     - list sliced files
  slice UPLOADEDID [-c CFG] - slice an uploaded STL [and use CFG config file]
  get SLICEDID              - downloaded sliced GCode
  """

def run(sock):
  if '-h' in sys.argv:
    show_help()
    exit(2)

  if 'import' in sys.argv:
    i = sys.argv.index('import') + 1
    with open(sys.argv[i]) as fin:
      fdata = fin.read()
    data = {'cmd': 'import',
        'data': base64.encodestring(fdata),
        'name': base64.encodestring(sys.argv[i])}
  elif 'importconfig' in sys.argv:
    i = sys.argv.index('importconfig') + 1
    with open(sys.argv[i]) as fin:
      fdata = fin.read()
    data = {'cmd': 'importconfig',
        'data': base64.encodestring(fdata),
        'name': base64.encodestring(sys.argv[i])}

  elif 'ping' in sys.argv:
    data = {'cmd': 'ping', 'c': 0}

  elif 'listi' in sys.argv:
    data = {'cmd': 'listimported'}
  elif 'listc' in sys.argv:
    data = {'cmd': 'listconfig'}
  elif 'slice' in sys.argv:
    i = sys.argv.index('slice') + 1
    if '-c' in sys.argv[i+1:]:
      cfg = sys.argv[i+2]
      data = {'cmd': 'slice', 'id': sys.argv[i], 'cfg': cfg}
    else:
      data = {'cmd': 'slice', 'id': sys.argv[i]}


  elif 'listd' in sys.argv:
    data = {'cmd': 'listdone'}
  elif 'get' in sys.argv:
    i = sys.argv.index('get') + 1
    data = {'cmd': 'getdone', 'id': sys.argv[i]}
  else:
    print 'unknown command parameters'
    print
    show_help()
    exit(3)

  ret = talkto(data, sock)
  if ret.has_key(u'm'):
    print ret['m']
  if ret.has_key('files'):
    print 'Response:'
    for f in ret['files']:
      print base64.decodestring(f['nm']), '-', 'id:', f['id'], 'size:', f['sz']

  if 'get' in sys.argv and ret.has_key(u'data'):
    fdata = base64.decodestring(ret['data'])
    with open(sys.argv[i], 'w+') as fin:
      fin.write(fdata)


if __name__=="__main__":
  HOST, PORT = "::1", 9999

  # Create a socket (SOCK_STREAM means a TCP socket)
  sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))

  try:
    run(sock)
  finally:
    sock.close()
