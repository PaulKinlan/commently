import functools
import logging

from google.appengine.api import memcache

def cache(name = "", timeout = 10):
  def factory(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
      key = repr(args) + repr(kwargs)
    
      result = memcache.get('%s:%s' % (name, key)) 
    
      if not result:
        result = func(self, *args, **kwargs)
        memcache.add('%s:%s' % (name, key), result, timeout)	
    
      return result
    return wrapper
  return factory
  
  
  
def cors(func):
  '''
  Enables CORS on WebRequests
  '''
  @functools.wraps(func):
  def wrapper(self, *args, **kwargs):
    self.response.headers["Access-Control-Allow-Origin"] = "*"
    return func(self, *args, **kwargs)
  
  return wrapper