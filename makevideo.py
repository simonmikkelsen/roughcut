#! /usr/bin/python

import sys
import os.path
import json
import subprocess
import infomerger

class MkVideo:
  def __init__(self, infofiles):
    self.infofiles = infofiles

  def mkMltXml(self):
    filenames = []
    inouts = []
    for f in self.infofiles:
      reader = infomerger.InfoReader(f)
      filenames.append(reader.getFilename())
      merger = reader.getMerger()
      mergedInfo = merger.mergeInfo()
      inouts.append(self.filter(mergedInfo))

    header = self.getHeader(filenames)
    body = self.getBody(inouts)
    footer = self.getFooter()
    return "\n".join([header, body, footer])

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

  def getHeader(self, filenames):
    header = ["<mlt>"]
    i = 0
    for name in filenames:
      header.append("""    <producer id="producer%s">
        <property name="resource">%s</property>
    </producer>""" % (i, name))
      i = i + 1
    header.append('    <playlist id="playlist0">')
    return "\n".join(header)

  def getBody(self, inouts):
    body = [] 
    i = 0
    for inout in inouts:
      for io in inout:
	body.append("""        <entry producer="producer%s" in="%s" out="%s"/>""" % (i, io['in'], io['out']))
      i = i + 1
    return "\n".join(body)
    
  def getFooter(self):
    return "    </playlist>\n</mlt>"

class MltRunner:
  def __init__(self, outputfile):
    self.outputfile = outputfile
  def getMltFile(self):
    mltfile = self.outputfile
    if self.outputfile.find(".") != -1:
      mltfile = self.outputfile[:self.outputfile.find(".")]
      mltfile = mltfile + ".mlt"
    return mltfile
  def run(self):
    args = ["melt", self.getMltFile(), "-consumer", "avformat:%s" % self.outputfile]
    subprocess.call(args)

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "Usage: outputfile.mp4 meta-file [meta-file...]"
    sys.exit(1)
  outputfile = sys.argv[1]
  runner = MltRunner(outputfile)

  infofiles = sys.argv[2:]
  for f in infofiles:
    if not os.path.isfile(f):
      print "The given filename '%s' does not exist." % f

  mkvid = MkVideo(infofiles)
  mltXml = mkvid.mkMltXml()
  meltfile = runner.getMltFile()
  fp = open(meltfile, "w")
  fp.write(mltXml)
  fp.close()

  runner.run()

