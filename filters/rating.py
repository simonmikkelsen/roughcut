
class RatingFilter:
  def __init__(self, rating):
    self.rating = rating

  def filter(self, mergedInfo):
    latestFrame = -1
    latestGood = -1
    minRating = self.rating
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
