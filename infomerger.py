#! /usr/bin/python

import sys
import os.path
import json

class InfoReader:
  def __init__(self, filename):
    self.filename = filename
    fp = open(self.filename, "r")
    self.info = json.load(fp)
    fp.close()

  def getInfo(self):
    return self.info
  
  def getMerger(self):
    info = self.getInfo()
    return InfoMerger(info)

  def getFilename(self):
    return self.info['filename']
    

class InfoMerger:
  def __init__(self, info):
    self.info = info

  def mergeInfo(self):
    merged = []
    prevFrameNo = -1
    for entry in self.info['frames']:
      frameno = entry['frameno']
      if frameno < prevFrameNo:
        i = 0
        for m in merged:
          if m['frameno'] > frameno:
            break
          else:
            i = i + 1
        merged = merged[:i]
      prevFrameNo = frameno
      merged.append(entry)
    return merged


if __name__ == "__main__":
  filename = sys.argv[1]
  if not os.path.isfile(filename):
    print "The given filename '%s' does not exist." % filename
  infoReader = InfoReader(filename)
  merger = infoReader.getMerger()
  print merger.mergeInfo()


