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
import time
import logging
logging.basicConfig(filename='/var/log/deslicer.log',level=logging.DEBUG)

def logaccess(dn, up, cmd, con):
  con.execute(u'''
    insert into stats(cmd, timestamp, sent, recvd) values (?, DateTime(\'now\'), ?, ?)
    ''', (cmd,up,dn))
  con.commit()


#def logaccess(cmd, con):
#  con.execute(u'''
#    insert into stats(cmd, timestamp) values (?, DateTime(\'now\'))
#    ''', (cmd,))
#  con.commit()
#
#def logtraffic(size, con, sent = True):
#  con.execute(u'''
#    insert into stats({}, timestamp) values (?, DateTime(\'now\'))
#    '''.format('sent' if sent else 'recvd'), (size,))
#  con.commit()

def importit(j, con):
  if j.has_key('data'):
    fname = os.path.join('stl',str(uuid.uuid1())+'.stl')
    with open(fname, 'w+') as fin:
      fin.write(decodestring(j['data']))
    with con:
      con.execute(u'insert into stl(localname, origname) values (?, ?)',
        (fname, j['name']))
      con.commit()
  return {'r': 'ok',
      'm': 'recieved {} B'.format(len(j['data'])),
      'id': fname}

def listimported(j, con):
  files = os.listdir('stl')
  stats = map(lambda x: os.stat(os.path.join('stl', x)), files)

  cur = con.cursor()
  a = cur.execute('select * from stl')
  nms = dict(map(lambda x: (x['localname'], x['origname']), a))

  return {'files': map(lambda (x,y): {'id': x, 'sz': y.st_size,
    'mtime': y.st_mtime, 'nm': nms['stl/'+x]}, zip(files, stats))}

def importconfig(j, con):
  if j.has_key('data'):
    fname = os.path.join('cfg',str(uuid.uuid1())+'.cfg')
    with open(fname, 'w+') as fin:
      fin.write(decodestring(j['data']))
    with con:
      con.execute(u'insert into configs(localname, origname) values (?, ?)',
        (fname, j['name']))
      con.commit()
  return {'r': 'ok',
      'm': 'recieved {} B'.format(len(j['data'])),
      'id': fname}

def listconfigs(j, con):
  files = os.listdir('cfg')
  stats = map(lambda x: os.stat(os.path.join('cfg', x)), files)

  cur = con.cursor()
  a = cur.execute(u'select * from configs')
  nms = dict(map(lambda x: (x['localname'], x['origname']), a))

  logging.info('in db:' + repr(nms))
  return {'files': map(lambda (x,y): {'id': x, 'sz': y.st_size,
    'mtime': y.st_mtime, 'nm': nms['cfg/'+x]}, zip(files, stats))}

def listdone(j, con):
  files = os.listdir('gcode')
  stats = map(lambda x: os.stat(os.path.join('gcode', x)), files)
  return {'files': map(lambda (x,y): {'id': x, 'sz': y.st_size,
    'mtime': y.st_mtime, 'nm': encodestring(x)}, zip(files, stats))}

def getdone(j, con):
  idx = os.path.basename(j['id'])
  name = os.path.join(os.path.abspath('gcode'), idx)

  if os.path.isfile(name):
    with open(name) as fin:
      data = encodestring(fin.read())

    return {'data': data, 'size': len(data), 'r': 'ok', 'm': 'ok', 'name': idx}
  else:
    return {'r': 'fail', 'm': 'file "{}" not found'.format(name)}

def listprogress(j, con):
  files = os.listdir('work')
  stats = map(lambda x: os.stat(os.path.join('work', x)), files)
  return {'files': map(lambda (x,y): {'id': x, 'sz': y.st_size,
    'mtime': y.st_mtime, 'nm': encodestring(x)}, zip(files, stats))}

def noop(j, con):
  return {}

def ping(j, con):
  return {'r': 'pong', 'm': 'pong', 'c':int(j['c'])+1}


def slicethread(fname, oname, wname, cfg, jobid):
  retcode = "fail"
  try:
    con = sqlite3.connect('db.sqlite')
    con.row_factory = sqlite3.Row

    cfg = "config.ini" if cfg is None else cfg

    proc = subprocess.Popen(["slic3r",
      "--load", cfg,
      fname, "-o", wname+'.gcode'])
    con.execute('insert into journal(cmd, pid, action, status, timestamp) values(?,?,?,?,DateTime(\'now\'))',
      ('slice {} -c {}'.format(os.path.basename(fname),
                               os.path.basename(cfg)), proc.pid, 'start',
        0 if proc.returncode == None else 1 ))
    con.commit()
    retcode = proc.wait()
    con.execute('insert into journal(cmd, pid, action, status, timestamp) values(?,?,?,?,DateTime(\'now\'))',
      ('slice {} -c {}'.format(os.path.basename(fname),
                               os.path.basename(cfg)), proc.pid, 'stop',
        proc.returncode))
    con.commit()
    try:
      os.unlink(oname+'.gcode')
    except OSError as e:
      pass
    finally:
      try:
        os.rename(wname+'.gcode', oname+'.gcode')
      except Exception:
        logging.info( wname+'.gcode')
        logging.info( oname+'.gcode')
        pass
  finally:
    _work_done(jobid, val=retcode)


def _seq():
  s = 0
  while True:
    yield s
    s += 1

from threading import Lock
_task_lock = Lock()
_task_list = dict()
_task_seq = _seq()
def _work_reg():
  _task_lock.acquire()
  jid = _task_seq.next()
  _task_list[jid] = False
  logging.info(str(_task_list))
  _task_lock.release()
  return jid

def _work_done(idx, val=None):
  _task_lock.acquire()
  if _task_list.has_key(idx):
    _task_list[idx] = True if val is None else val
  logging.info(str(_task_list))
  _task_lock.release()

def is_done(idx):
  _task_lock.acquire()

  if _task_list.has_key(idx):
    st = _task_list[idx]
  else:
    st = None
  logging.info(str(_task_list))
  _task_lock.release()

  return st


def sliceit(j, con):
  idx = os.path.basename(j['id'])
  oname = os.path.join(os.path.abspath('gcode'), idx)
  wname = os.path.join(os.path.abspath('work'), idx)
  fname = os.path.join(os.path.abspath('stl'), idx)
  logging.info("{} {} {}".format(fname, oname, wname))
  cfg = None
  if j.has_key('cfg'):
    cfg = 'cfg/'+os.path.basename(j['cfg'])

  jobid = _work_reg()
  th = threading.Thread(target=slicethread, args=(fname, oname, wname, cfg, jobid))
  th.start()

  return {'m': 'slicing started. job id: {}'.format(jobid),
      'r': 'ok', 'jobid': jobid}

def getstats(j, con):
  r = tuple(con.execute(u'select count(cmd) as cnt, sum(recvd) as recvd, sum(sent) as sent from stats;'))
  return {'r': 'ok', 'm': 'ok', 'cnt': r[0][0],
      'rcv': r[0][1], 'snt': r[0][2]}

def getjournal(j, con):
  r = con.execute(u'select * from journal order by timestamp desc limit 6;')
  return {'r': 'ok', 'm': 'ok', 'data': list(map(dict,r))}

def wipefile(j, con):
  typ = j['typ']
  idx = j['idx']
  d = {'stl': 'stl', 'cfg': 'cfg', 'done': 'gcode'}
  if typ in d.keys():
    fname = os.path.basename(idx)
    fname = os.path.join(d[typ], fname)

    logging.info('LALALALA')
    if os.path.exists(fname):
      os.unlink(fname)
      return {'r': 'ok', 'm': '{}/{} deleted'.format(typ, idx)}
    else:
      return {'r': 'fail', 'm': '{}/{} doesnt exist'.format(typ, idx)}
  else:
    return {'r': 'fail', 'm': 'invalid type: {}'.format(typ)}

def waitfor(j, con):
  jobid = int(j['jobid'])
  r = False
  while r is False:
    r = is_done(jobid)
    time.sleep(1)
  return {'r': 'ok', 'm': 'ended with status {}'.format(r)
      if not r is None else 'job doesnt exist', 'status': r}


def handle(data, con, apikey=None):
  d = json.loads(data)

  handlers = {'import': importit, 'ping': ping,
      'listimported': listimported, 'slice': sliceit,
      'listdone': listdone, 'getdone': getdone,
      'importconfig': importconfig, 'listconfig': listconfigs,
      'listprogress': listprogress, 'getstats': getstats,
      'journal': getjournal, 'del': wipefile, 'wait': waitfor}

  hndlr = noop
  cmd = 'noop'
  if d.has_key('cmd'):
    if d['cmd'] in handlers.keys():
      cmd = d['cmd']
      hndlr = handlers[cmd]

  logging.info('cmd: ' + cmd)

  if not apikey is None:
    if not (d.has_key('key') and d['key'] == apikey):
      logging.info('authentication failed for "{}" key!'.format(
        '' if not d.has_key('key') else d['key']))
      return json.dumps({'r': 'fail',
        'm': 'authentication failed. incorrect apikey'})

  try:
    r = hndlr(d, con)
    result = json.dumps(r)
  except Exception as e:
    logging.error(str(e))
    result = json.dumps({u'm':unicode(e), u'r':u'fail'})
  logaccess(len(d), len(result), unicode(cmd), con)

  return result
