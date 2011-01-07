from google.appengine.ext import db

import hashlib
import simplejson

class Activity(db.Model):
  '''
  Key - id
  '''
  id = db.StringProperty()
  data = db.TextProperty()
  last_updated = db.DateTimeProperty(auto_now = True)
  
  @staticmethod
  def Get(username, title):
    
    m = hashlib.md5()
    m.update(username + title)
    key = m.hexdigest()
    
    return Activity.get_by_key_name(key)
    
  @staticmethod
  def Put(username, title, activity):
    
    m = hashlib.md5()
    m.update(username + title)
    key = m.hexdigest()
    
    act = Activity(key_name = key)
    
    act.id = activity["id"]
    act.data = simplejson.dumps(activity)
    
    act.put()