import json
import uuid
from base64 import (
    decodestring,
    encodestring
    )
import os
import threading
import subprocess
import sqlite3


def importit(j, con):
  if j.has_key('data'):
    fname = os.path.join('stl',str(uuid.uuid1())+'.stl')
    with open(fname, 'w+') as fin:
      fin.write(decodestring(j['data']))
    with con:
      con.execute(u'insert into stl(localname, origname) values (?, ?)',
        (fname, j['name']))
  return {'r': 'ok',
      'm': 'recieved {} B'.format(len(j['data'])),
      'id': fname}

def listimported(j, con):
  files = os.listdir('stl')
  sizes = map(lambda x: os.stat(os.path.join('stl', x)).st_size, files)

  cur = con.cursor()
  a = cur.execute('select * from stl')
  nms = dict(map(lambda x: (x['localname'], x['origname']), a))

  return {'files': map(lambda (x,y): {'id': x, 'sz': y, 'nm': encodestring(nms['stl/'+x])}, zip(files, sizes))}

def importconfig(j, con):
  if j.has_key('data'):
    fname = os.path.join('cfg',str(uuid.uuid1())+'.cfg')
    with open(fname, 'w+') as fin:
      fin.write(decodestring(j['data']))
    with con:
      con.execute(u'insert into configs(localname, origname) values (?, ?)',
        (fname, j['name']))
  return {'r': 'ok',
      'm': 'recieved {} B'.format(len(j['data'])),
      'id': fname}

def listconfigs(j, con):
  files = os.listdir('cfg')
  sizes = map(lambda x: os.stat(os.path.join('cfg', x)).st_size, files)

  cur = con.cursor()
  a = cur.execute(u'select * from configs')
  nms = dict(map(lambda x: (x['localname'], x['origname']), a))

  print 'in db:', nms
  return {'files': map(lambda (x,y): {'id': x, 'sz': y, 'nm': nms['cfg/'+x]}, zip(files, sizes))}

def listdone(j, con):
  files = os.listdir('gcode')
  sizes = map(lambda x: os.stat(os.path.join('gcode', x)).st_size, files)
  return {'files': map(lambda (x,y): {'id': x, 'sz': y, 'nm': encodestring(x)}, zip(files, sizes))}

def getdone(j, con):
  idx = j['id']
  name = os.path.join(os.path.abspath('gcode'), idx)

  if os.path.isfile(name):
    with open(name) as fin:
      data = encodestring(fin.read())

    return {'data': data, 'size': len(data), 'r': 'ok', 'm': 'ok', 'name': idx}
  else:
    return {'r': 'fail', 'm': 'file "{}" not found'.format(name)}

def noop(j, con):
  return {}

def ping(j, con):
  return {'r': 'pong', 'm': 'pong', 'c':int(j['c'])+1}


def slicethread(fname, oname, cfg):
  retcode = subprocess.call(["slic3r",
    "--load", "config.ini" if cfg is None else cfg,
    fname, "-o", oname+'.gcode'])

def sliceit(j, con):
  idx = j['id']
  oname = os.path.join(os.path.abspath('gcode'), idx)
  fname = os.path.join(os.path.abspath('stl'), idx)
  cfg = None
  if j.has_key('cfg'):
    cfg = 'cfg/'+j['cfg']
  th = threading.Thread(target=slicethread, args=(fname, oname, cfg))
  th.start()
  return {'m': 'slicing started', 'r': 'ok'}


def handle(data, con):
  d = json.loads(data)

  handlers = {'import': importit, 'ping': ping,
      'listimported': listimported, 'slice': sliceit,
      'listdone': listdone, 'getdone': getdone,
      'importconfig': importconfig, 'listconfig': listconfigs}

  if d.has_key('cmd'):
    if d['cmd'] in handlers.keys():
      hndlr = handlers[d['cmd']]
    else:
      hndlr = noop

  r = hndlr(d, con)


  return json.dumps(r)
