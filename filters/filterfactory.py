import lib.optparser
import filters.rating

class FilterFactory:
  def __init__(self):
    pass
  def create(slef, filtername, options = []):
    opt = lib.optparser.OptParser("profiles/"+filtername)
    opt.parse()
    options = opt.getContent()
    #TODO this is more a class name.
    filterNameInternal = options['filter']

    if filterNameInternal == 'rating':
      return filters.rating.RatingFilter(options['rating'])
    else:
      print "Unsupported filter: "+filterNameInternal
    
    
