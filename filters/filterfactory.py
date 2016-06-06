import os
import os.path

import lib.optparser
import filters.rating
import filters.intelli

class FilterFactory:
  def __init__(self):
    pass
  def create(slef, profilename, options = []):
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    opt = lib.optparser.OptParser(os.path.join(scriptdir, "..", "profiles", profilename))
    opt.parse()
    options = opt.getContent()
    filterName = options['filter']

    if filterName == 'rating':
      return filters.rating.RatingFilter(options['rating'])
    elif filterName == 'intelli':
      return filters.intelli.IntelliFilter(options)
    else:
      print "Unsupported filter: '%s'." % filterName
    
    
