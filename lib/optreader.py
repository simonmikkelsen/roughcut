class OptReader:
  def __init__(self, options):
    self.options = options
  def get(self, key):
    if not key in self.options:
      return None
    return self.options[key]
  def getInt(self, key):
    val = self.get(key)
    if val != None:
      return int(val)
    else:
      return None
