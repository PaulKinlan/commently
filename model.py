from google.appengine.ext import db

import hashlib
import simplejson
import settings

class Activity(db.Model):
  '''
  Key - id
  '''
  id = db.StringProperty()
  shortcut = db.StringProperty()
  username = db.StringProperty()
  data = db.TextProperty()
  title = db.StringProperty()
  last_updated = db.DateTimeProperty(auto_now = True)
  url = db.StringProperty()
  replies_url = db.StringProperty()
  likes_url = db.StringProperty()
  
  @staticmethod
  def Get(*args, **kwargs):
    q = db.Query(Activity)
    
    
    # build the filter dynamically, have to watch out for index errors.
    for key in kwargs:
      if key in settings.FILTER_MAP:
        newKey = settings.FILTER_MAP[key]
        q = q.filter("%s =" % newKey, kwargs[key])
    
    return q.get()
    
  @staticmethod
  def Put(activity):
    
    m = hashlib.md5()
    m.update(activity["id"])
    key = m.hexdigest()
    
    data = {
      "id" : activity["id"],
      "username": activity["actor"]["profileUrl"],
      "shortcut" : key,
      "title": activity["title"],
      "data" : simplejson.dumps(activity),
      "url" : activity["links"]["self"][0]["href"].replace("alt=json", ""),
      "replies_url" : activity["links"]["replies"][0]["href"].replace("alt=json", ""),
      "likes_url" : activity["links"]["liked"][0]["href"].replace("alt=json", "")
    }
    
    act = Activity.get_or_insert(key_name = key, **data)
    