#!/usr/bin/python

import sys
import os
import os.path
import json
import exiftool

class ExifReader:
  def __init__(self):
    self.exiftool = exiftool.ExifTool()
    self.exiftool.start()

  def read(self, mediaPath):
    self.metadata = self.exiftool.get_metadata(mediaPath)

  def get(self, key):
    if key in self.metadata:
      return self.metadata[key]
    else:
      return None
  def getOneOf(self, keys):
    for keyToFind in keys:
      for key in self.metadata.keys():
	if key.endswith(keyToFind):
          return self.metadata[key]
    return None

  def getCreateDate(self):
    return self.getOneOf(['CreateDate', 'DateTimeOriginal'])
  def getFrameRate(self):
    return self.getOneOf(['FrameRate'])
  def getDuration(self):
    return self.getOneOf(['Duration'])

class MediaIndexer:
  def __init__(self, paths):
    self.paths = paths 
    self.extensions = ('.mp4', '.mts', '.mov', '.avi', '.mpg', '.wav', '.mp3', '.gpx')
    self.exifReader = ExifReader()
  def doIndex(self):
    for path in paths:
      for dirName, subdirList, fileList in os.walk(path):
        if dirName.find("\n") == -1:
          for fname in fileList:
            if fname.lower().endswith(self.extensions):
              self.registerMedia(os.path.join(dirName, fname))

  def registerMedia(self, mediaPath):
    self.exifReader.read(mediaPath)
    print "Date, duration, framerate"
    print self.exifReader.getCreateDate()
    print self.exifReader.getDuration()
    print self.exifReader.getFrameRate()
    print mediaPath
    print

    # QuickTime:CreateDate
    # QuickTime:TrackDuration
    # QuickTime:VideoFrameRate
    # H264:DateTimeOriginal
    # H264:CaptureFrameRate
    # H264:VideoFrameRate
    # M2TS:Duration


if __name__ == "__main__":
  paths = sys.argv[1:]
  indexer = MediaIndexer(paths)
  indexer.doIndex()
