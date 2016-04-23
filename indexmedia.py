#!/usr/bin/python

import sys
import os
import os.path
import json
import exiftool


class MediaIndexer:
  def __init__(self, paths):
    self.paths = paths 
    self.extensions = ('.mp4', '.mts', '.mov', '.avi', '.mpg', '.wav', '.mp3', '.gpx')
    self.exiftool = exiftool.ExifTool()
    self.exiftool.start()
  def doIndex(self):
    for path in paths:
      for dirName, subdirList, fileList in os.walk(path):
        if dirName.find("\n") == -1:
          for fname in fileList:
            if fname.lower().endswith(self.extensions):
              self.registerMedia(os.path.join(dirName, fname))

  def registerMedia(self, mediaPath):
    print self.exiftool.get_metadata(mediaPath)
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
