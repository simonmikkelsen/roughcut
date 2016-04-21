#! /usr/bin/python

import sys
import os.path
import json
import infomerger

class MkVideo:
  def __init__(self, infofile):
    self.infofile = infofile 
    self.infoReader = infomerger.InfoReader(infofile)

  def mkMltXml(self):
    merger = self.infoReader.getMerger()
    mergedInfo = merger.mergeInfo()
    header = self.getHeader()
    body = self.getBody(self.filter(mergedInfo))
    footer = self.getFooter()
    return header + body + footer

  def filter(self, mergedInfo):
    latestFrame = -1
    latestGood = -1
    minRating = 4
    inout = []
    for info in mergedInfo:
      if info['rating'] >= minRating:
        if latestFrame < 0:
          latestFrame = info['frameno']
        else:
          latestGood = info['frameno']
      else:
        if latestFrame >= 0:
          inout.append({'in':latestFrame, 'out':info['frameno']})
          latestFrame = -1
    if latestFrame >= 0 and latestgood >= 0:
      inout.append({'in':latestFrame, 'out':latestGood})

    return inout

  def getHeader(self):
    return """<mlt>
<producer id="producer0">
       <property name="resource">%s</property>
            </producer>
            <playlist id="playlist0">
""" % self.infoReader.getOriginalFilename()

  def getBody(self, inout):
    body = ""
    for io in inout:
      body = body + """                <entry producer="producer0" in="%s" out="%s"/>\n""" % (io['in'], io['out'])
    return body
    
  def getFooter(self):
    return "  </playlist>\n</mlt>"

if __name__ == "__main__":
  infofile = sys.argv[1]
  if not os.path.isfile(infofile):
    print "The given filename '%s' does not exist." % infofile

  mkvid = MkVideo(infofile)
  mltXml = mkvid.mkMltXml()
  print mltXml
