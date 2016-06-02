import lib.optreader
class IntelliFilter:
  def __init__(self, options):
    self.opt = lib.optreader.OptReader(options)

  def filter(self, mergedInfo, framerate = 24):
    session = IntelliFilterSession(self.opt, mergedInfo, framerate)
    return session.filter()
class IntelliFilterSession:
  def __init__(self, options, mergedInfo, framerate):
    self.options = options
    self.mergedInfo = mergedInfo
    self.framerate = framerate
  def filter(self):
    minRating = self.options.getInt('minrating')
    if minRating != None and minRating > 0:
      self.filterByRating(minRating)

    clipsize = self.options.getInt('clipSize')
    maxlength = self.options.getInt('maxlength')
    if maxlength != None and maxlength > 0:
      self.applyMaxLength(maxlength)

    return self.mergedInfo
  def sec2Frame(self, secs):
    return int(secs * self.framerate)
  def frame2Sec(self, frames):
    return int(frames / self.framerate)
  def size(self, info):
    return info['out'] - info['in']
  def shorten(self, info, framesToRemove):
    removeFromOut = int(framesToRemove / 2)
    removeFromIn = framesToRemove - removeFromOut
    info['out'] = info['out'] - removeFromOut
    info['in'] = info['in'] - removeFromIn

    return info

  def applyMaxLength(self, maxSeconds):
    totalFrames = 0
    for info in self.mergedInfo:
      totalFrames = totalFrames + self.size(info)
    maxFrames = self.sec2Frame(maxSeconds)
    if totalFrames <= maxFrames:
      return

    excessFrames = totalFrames - maxFrames
    ratio = float(excessFrames) / float(maxFrames)

    finalInfo = []
    framesLeftToRemove = excessFrames
    for info in self.mergedInfo:
      framesToRemove = int(self.size(info) * ratio)
      framesLeftToRemove =- framesToRemove
      finalInfo.append(self.shorten(info, framesToRemove))
    self.mergedInfo = finalInfo
    

  def filterByRating(self, minRating):
    latestFrame = -1
    latestGood = -1
    inout = []
    for info in self.mergedInfo:
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

    self.mergedInfo = inout
