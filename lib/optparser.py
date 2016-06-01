class OptParser:
  """Parses the options in the given file and allowed for the content to be returned.
The file is expected to contain key/value pairs. Empty lines, and lines where first non
white space is a # are ignored.
"""
  def __init__(self, filename):
    self.filename = filename
  
  def parse(self):
    myvars = {}
    with open(self.filename) as myfile:
      for line in myfile:
        if line.strip().startswith('#') or len(line.strip()) == 0:
          continue
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var.strip()
    self.content = myvars
  def getContent(self):
    return self.content

if __name__ == '__main__':
  import sys
  parser = OptParser(sys.argv[1])
  parser.parse()
  print parser.getContent()
