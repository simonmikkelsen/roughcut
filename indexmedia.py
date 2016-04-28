#!/usr/bin/python

import sys
import os
import os.path
import json
import calendar

import exiftool
import iso8601

import qhvsqlite

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
    date = self.getOneOf(['CreateDate', 'DateTimeOriginal'])
    # Input e.g.: 2016:01:01 15:52:45+01:00
    date = date.replace(":", "-", 2)
    try:
      dateTimeObj = iso8601.parse_date(date)
    except iso8601.iso8601.ParseError, e:
      print e
      return -1
    unixtime = calendar.timegm(dateTimeObj.utctimetuple())
    return unixtime

  def getFrameRate(self):
    return self.getOneOf(['FrameRate'])
  def getDuration(self):
    return self.getOneOf(['Duration'])

class MediaIndexer:
  def __init__(self, paths):
    self.paths = paths 
    self.videoExtensions = ('.mp4', '.mts', '.mov', '.avi', '.mpg' )
    self.audioExtensions = ('.wav', '.mp3')
    self.locationExtensions = ('.gpx')
    self.imageExtensions = ('.jpg', '.cr2', '.png', '.tif', '.tiff', '.gif')
    self.extensions = self.videoExtensions

    self.exifReader = ExifReader()
    self.data = qhvsqlite.QHVData()

  def doIndex(self):
    try:
      for path in paths:
        for dirName, subdirList, fileList in os.walk(path):
          if dirName.find("\n") == -1:
            for fname in fileList:
              if fname.lower().endswith(self.extensions):
                self.registerMedia(os.path.join(dirName, fname))
    finally:
      self.data.close()

  def registerMedia(self, mediaPath):
    if self.data.isRegistered(mediaPath):
      print "Skip: "+mediaPath
      return
    name = mediaPath.lower()
    if name.endswith(self.videoExtensions):
      self.registerVideo(mediaPath)

  def registerVideo(self, mediaPath):
    self.exifReader.read(mediaPath)
    print "Date, duration, framerate"
    print self.exifReader.getCreateDate()
    print self.exifReader.getDuration()
    print self.exifReader.getFrameRate()
    print mediaPath
    maxrating = -1
    self.data.addVideo(mediaPath, self.exifReader.getDuration(), self.exifReader.getFrameRate(), self.exifReader.getCreateDate(), maxrating)
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
