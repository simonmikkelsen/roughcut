#! /usr/bin/python

import sys
import os.path
import json
import subprocess
import getopt
import lib.infomerger as infomerger
import filters.rating as rating

class MkVideo:
  def __init__(self, filterClass, infofiles):
    self.infofiles = infofiles
    self.filterClass = filterClass

  def mkMltXml(self):
    filenames = []
    inouts = []
    for f in self.infofiles:
      reader = infomerger.InfoReader(f)
      filenames.append(reader.getFilename())
      merger = reader.getMerger()
      mergedInfo = merger.mergeInfo()
      #inouts.append(self.filter(mergedInfo))
      inouts.append(self.filterClass.filter(mergedInfo))

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
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:",
                  ["help", "profile="])
  except getopt.GetoptError, err:
    print str(err)
    sys.exit(2)

  profile = "rating"
  for switch, value in opts:
    if switch in ("-h", "--help"):
      print """Usage: [-h|-p] outputfile.mp4 meta-file [meta-file...]
-h --help     Show this help.
-p --profile= Give the name of the profile to use. See profiles in the profile dir."""
    elif switch in "-f", "--profile"):
      profile = value


  if len(args) < 2:
    print "You must at least give an output file and a meta file."
    sys.exit(1)
  outputfile = args[0]
  if os.path.isfile(outputfile):
      print "Outputfile '%s' already exists." % outputfil
      sys.exit()
  runner = MltRunner(outputfile)

  infofiles = args[1:]
  for f in infofiles:
    if not os.path.isfile(f):
      print "The given filename '%s' does not exist." % f

  mkvid = MkVideo(rating.RatingFilter(4), infofiles)
  mltXml = mkvid.mkMltXml()
  meltfile = runner.getMltFile()
  fp = open(meltfile, "w")
  fp.write(mltXml)
  fp.close()

  #runner.run()

