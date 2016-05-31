class OptParser:
  def __init__(self, filename):
    self.filename = filename
  
  def parse(self):
    myvars = {}
    with open(filename) as myfile:
      for line in myfile:
        if line.strip().startswith('#'):
i         continue
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var
