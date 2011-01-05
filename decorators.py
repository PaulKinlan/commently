import functools
import logging

from google.appengine.api import memcache

def cache(func, name, timeout = 10):
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    key = repr(args) + repr(kwargs)
    
    result = memcache.get('%s:%s' % (name, key)) 
    
    if not result:
      result = func(self, *args, **kwargs)
      memcache.add('%s:%s' % (name, key), result, timeout)	
    
    return result
  return wrapper