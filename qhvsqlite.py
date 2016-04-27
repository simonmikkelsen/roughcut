#!/usr/bin/python 

import sqlite3 as sq
import os.path

class QHVData:
  def __init__(self):
    self.conn = sq.connect('test.db')
    self.cur = self.conn.cursor()
    self.cur.execute('CREATE TABLE IF NOT EXISTS MEDIA (filename TEXT, fullpath TEXT UNIQUE, starttime INTEGER, endtime INTEGER, duration INTEGER)')
    self.cur.execute("""CREATE TABLE IF NOT EXISTS VIDEO (media_id INTEGER,
                   framerate NUMERIC, maxrating INTEGER)""")
    #               FOREIGN KEY(media_id) REFERENCES MEDIA(rowid));""")
  def isRegistered(self, fullpath):
    self.cur.execute('SELECT count(*) FROM MEDIA WHERE fullpath = ?', (fullpath,))
    res = self.cur.fetchone()
    return res[0] > 0

  def addVideo(self, fullpath, duration, framerate, starttime, maxrating):
    filename = os.path.basename(fullpath)
    endtime = -1
    if starttime != None and duration != None:
      endtime = starttime + duration

    if duration == None:
      duration = -1

    self.cur.execute('INSERT INTO MEDIA (filename, fullpath, starttime, endtime, duration) VALUES (?, ?, ?, ?, ?)',
      (filename, fullpath, starttime, endtime, duration))
    mediaid = self.cur.lastrowid

    self.cur.execute('INSERT INTO VIDEO (media_id, framerate, maxrating) VALUES (?, ?, ?)',
      (mediaid, framerate, maxrating))

    self.conn.commit()
  def close(self):
    if self.conn:
      self.conn.commit()
      self.conn.close()
