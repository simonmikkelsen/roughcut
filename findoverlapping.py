#!/usr/bin/python

import qhvsqlite

class OverlapFinder:
  def __init__(self):
    self.data = qhvsqlite.QHVData()
  
  def findOverlaps(self):
    allMedia = self.data.getAllMedia()
    overlaps = []
    # rowid, starttime, endtime
    for outMedia in allMedia:
      for inMedia in allMedia: 
        #dr2.start > dr1.start -- start after dr1 is started
        #dr2.start < dr1.end   -- start before dr1 is finished
        if inMedia[1] > outMedia[1] and inMedia[1] < outMedia[2]:
          overlapDuration = min(inMedia[2], outMedia[2])  - inMedia[1]
          if overlapDuration > 2:
            print "Overlap: " + str(overlapDuration)+" sec: " + str(outMedia[3]) + " / "  + str(inMedia[3])

if __name__ == "__main__":
  finder = OverlapFinder()
  print finder.findOverlaps()