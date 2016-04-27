#!/usr/bin/python 
import sqlite3 as sq

class QHVData:
  def __init__(self):
    self.conn = sq.connect('test.db')
    cur = self.conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS MEDIA (filename TEXT, fullpath TEXT UNIQUE)');
    cur.execute("""CREATE TABLE IF NOT EXISTS VIDEO (media_id INTEGER,
                   duration NUMERIC, framerate NUMERIC, starttime INTEGER, maxrating INTEGER,
                   FOREIGN KEY(media_id) REFERENCES MEDIA(rowid));""")
