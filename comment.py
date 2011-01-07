#!/usr/bin/env python
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
    return self.Fetch(settings.BUZZ_ACTIVITIES % (username))
  
  def Fetch(self, url):
    
    params = {
      "alt" : "json",
      "max-results" : settings.MAX_FETCH,
      "max-comments" : settings.MAX_FETCH,
      "max-liked" : settings.MAX_FETCH,
      "key" : settings.API_KEY
    }
    requestUrl = url + "&" + urllib.urlencode(params)
    logging.info(requestUrl)
    result = urlfetch.fetch(requestUrl, deadline = 30)
    data = result.content
    return simplejson.loads(data)
  
  @decorators.cache("BuzzProcess.FindActivity")
  def FindActivity(self, username, title):
    '''
    Finds an activity, once it is in the datastore, we never fetch it again,
    rather we subscribe to its pubsub feed.
    '''
    
    # get activity from data store,
    activity = model.Activity.Get(username, title)
    
    if activity:
      return simplejson.loads(activity.data)
    
    # nothing in the datastore, so lets fetch it.
    
    activities = self.FetchData(username)
    
    if not activities and not activities["data"]:
      return None
    
    data = activities["data"]["items"];
    for activity in data:
      # This is litterally the first bit that can't be done in JSONp
      if activity["title"] == title:
        # Save the data for 
        model.Activity.Put(username, title, activity)
        
        # Send off a task to handle pubsub
        taskqueue.add(queue_name = "subscribe",
          url='/tasks/activity/subscribe',
          params={ 
            "id" : activity["id"],
            "username" : username,
            "title" : title
          })
        
        return activity
    
    return None
  
  @decorators.cache("BuzzProcess.GetLikes")
  def GetLikes(self, activity):
    url = activity["links"]["liked"][0]["href"] 
    return self.Fetch(url)
    
  @decorators.cache("BuzzProcess.GetReplies")
  def GetReplies(self, activity):
    url = activity["links"]["replies"][0]["href"]
    return self.Fetch(url)
    
    
class CommentHandler(webapp.RequestHandler):
  def getActivity(self, username, title):
    activity = {}
    
    process = BuzzProcess()
    
    activity = process.FindActivity(username, title)
    
    return activity

class JSCommentHandler(CommentHandler):
  @decorators.cors
  def get(self, extension = "js"):
    title = urllib.unquote(self.request.get("title"))
    username = self.request.get("username")
    callback = self.request.get("callback")
    
    output = "{}"
    
    activity = self.getActivity(username, title)
    responsedata = simplejson.dumps(activity)
    
    # if there is no callback is specifed just return the data, XHR/CORS might
    # be being used.
    if not callback:
      output = responsedata
    else:
      output = "if(%s) { %s(%s); }" % (callback, callback, responsedata)
    
    self.response.headers["Content-Type"] = "application/javascript"
    self.response.out.write(output)
    
class HTMLCommentHandler(CommentHandler):
  @decorators.cors
  def get(self, extension = "js"):
    title = urllib.unquote(self.request.get("title"))
    username = self.request.get("username")
   
    activity = self.getActivity(username, title)
    
    self.response.headers["Content-Type"] = "text/html"
    path = os.path.join(os.path.dirname(__file__), "templates" ,'comments.tmpl')
    output = template.render(path, activity)
    self.response.out.write(output)