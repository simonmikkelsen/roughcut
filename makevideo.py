#! /usr/bin/python

import sys
import os.path
import json
import subprocess
import getopt
import lib.infomerger as infomerger
import filters.rating as rating
import filters.filterfactory as factory

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
      framerate = reader.getFrameRate()
      if framerate == None:
        # Currently OK guess.
        # TODO: Read from the file.
        framerate = 27
      inouts.append(self.filterClass.filter(mergedInfo, framerate))

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
    render = True
  def getMltFile(self):
    mltfile = self.outputfile
    if self.outputfile.find(".") != -1:
      mltfile = self.outputfile[:self.outputfile.find(".")]
      mltfile = mltfile + ".mlt"
    return mltfile
  def setRender(self, render):
    self.render = render
  def run(self):
    if self.render:
      args = ["melt", self.getMltFile(), "-consumer", "avformat:%s" % self.outputfile]
    else:
      args = ["melt", self.getMltFile()]
    subprocess.call(args)

if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:s",
                  ["help", "profile=", "show"])
  except getopt.GetoptError, err:
    print str(err)
    sys.exit(2)

  profile = "rating"
  render = True
  for switch, value in opts:
    if switch in ("-h", "--help"):
      print """Usage: [-h|-p|-s] outputfile.mp4 meta-file [meta-file...]
-h --help     Show this help.
-p --profile= Give the name of the profile to use. See profiles in the profile dir.
-s --show     Show the video instead of rendering it to a file.
              A fake output file must still be given, but it ignored.
              This makes previewing easier."""
    elif switch in ("-p", "--profile"):
      profile = value
    elif switch in ("-s", "--show"):
      render = False


  if len(args) < 2:
    print "You must at least give an output file and a meta file."
    sys.exit(1)
  outputfile = args[0]
  if os.path.isfile(outputfile):
      print "Outputfile '%s' already exists." % outputfile
      sys.exit()

  infofiles = args[1:]
  for f in infofiles:
    if not os.path.isfile(f):
      print "The given filename '%s' does not exist." % f

  filterFactory = factory.FilterFactory()
  filterClass = filterFactory.create(profile)

  runner = MltRunner(outputfile)
  runner.setRender(render)
  mkvid = MkVideo(filterClass, infofiles)
  mltXml = mkvid.mkMltXml()
  meltfile = runner.getMltFile()
  fp = open(meltfile, "w")
  fp.write(mltXml)
  fp.close()

  runner.run()

