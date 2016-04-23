#!/usr/bin/python

import sys
import os.path
import json

class MediaIndexer:
  def __init__(self, paths):
    self.paths = paths 
  def doIndex(self):
    for path in paths:
      print path


if __name__ == "__main__":
  paths = sys.argv[1:]
  indexer = MediaIndexer(paths)
