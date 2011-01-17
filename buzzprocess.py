#
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import taskqueue

from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

import simplejson
import settings
import decorators
import logging
import urllib
import os
import model

class BuzzProcess(object):
  
  def FetchData(self, username):
    return self.Fetch((settings.BUZZ_ACTIVITIES + "?") % (username))
    
  def GetProperty(self, prop, data):
    props = prop.replace(".", "\"][\"")
    
    command = "data[\"%s\"]" % props
    
    return eval(command )
  
  def Fetch(self, url):
    
    params = {
      "alt" : "json",
      "max-results" : settings.MAX_FETCH,
      "max-comments" : settings.MAX_FETCH,
      "max-liked" : settings.MAX_FETCH,
      "key" : settings.API_KEY
    }
    
    requestUrl = url + "&" + urllib.urlencode(params)
    logging.info("requesting %s" % requestUrl)
    result = urlfetch.fetch(requestUrl, deadline = 30)
    data = result.content
    
    return simplejson.loads(data)
  
  #@decorators.cache("BuzzProcess.FindActivity")
  def FindActivity(self, *args, **kwargs):
    '''
    Finds an activity, once it is in the datastore, we never fetch it again,
    rather we subscribe to its pubsub feed.
    '''
    
    username = kwargs["actor.profileUrl"].replace(settings.PROFILE_URL_ROOT, "")
        
    activities = self.FetchData(username)
    logging.info("Activities fetched: %s" % activities)

    try:
      data = activities["data"]["items"];
    except KeyError:
      logging.error("No activities retrieved for %s" % username)
      return None

    for activity in data:
      # This is literally the first bit that can't be done in JSONp
      mustAdd = False
      # exact match the attributes
      for attr in kwargs:
        if self.GetProperty(attr, activity) == kwargs[attr]:
          # We have a match, save the data for later
          mustAdd = True
        else:
          mustAdd = False
       
      if mustAdd: 
        model.Activity.Put(activity)
        # Send off a task to handle pubsub
        taskqueue.add(
          queue_name = "subscribe",
          url = '/tasks/feed/subscribe',
          params = { 
            "url" : (settings.BUZZ_ACTIVITIES + "?") % username
          })
      
        taskqueue.add(
          queue_name = "subscribe",
          url = '/tasks/feed/subscribe',
          params = { 
            "url" : activity["links"]["replies"][0]["href"].replace("?alt=json","")
          })
        
        return activity
    return None