import lib.optparser
import filters.rating
import filters.intelli

class FilterFactory:
  def __init__(self):
    pass
  def create(slef, profilename, options = []):
    opt = lib.optparser.OptParser("profiles/"+profilename)
    opt.parse()
    options = opt.getContent()
    filterName = options['filter']

    if filterName == 'rating':
      return filters.rating.RatingFilter(options['rating'])
    elif filterName == 'intelli':
      return filters.intelli.IntelliFilter(options)
    else:
      print "Unsupported filter: '%s'." % filterName
    
    
