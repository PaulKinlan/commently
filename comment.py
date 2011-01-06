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

from google.appengine.api import urlfetch

import simplejson
import settings
import decorators
import logging
import urllib

class BuzzProcess(object):
  
  def FetchData(self, username):
    return self.Fetch(settings.BUZZ_ACTIVITIES % (username))
    
  def Fetch(self, url):
    logging.info(url + "&" + settings.API_KEY)
    result = urlfetch.fetch(url + "&key=" + settings.API_KEY)
    data = result.content
    return simplejson.loads(data)
  
  #@decorators.cache
  def FindActivity(self, username, title):
    activities = self.FetchData(username)
    
    if not activities and not activities["data"]:
      return None
    
    data = activities["data"]["items"];
    for activity in data:
      if activity["title"] == title:
        return activity
    return None
  
  #@decorators.cache("likes", 10)
  def GetLikes(self, activity):
    url = activity["links"]["liked"][0]["href"] 
    return self.Fetch(url)
    
  #@decorators.cache("replies", 10)
  def GetReplies(self, activity):
    url = activity["links"]["replies"][0]["href"]
    return self.Fetch(url)

class CommentHandler(webapp.RequestHandler):
  def get(self):
    title = urllib.unquote(self.request.get("title"))
    username = self.request.get("username")
    callback = self.request.get("callback")
    
    process = BuzzProcess()
    
    activity = {}
    
    # if there is no callback use an empty handler
    if not callback:
      callback = "(function() {})();"
    else:
      activity = process.FindActivity(username, title)
      if activity:
        activity.update({"likes" : process.GetLikes(activity)})
        activity.update({"replies": process.GetReplies(activity)})
    
    responsedata = simplejson.dumps(activity)
    self.response.headers["Content-Type"] = "application/javascript"
    self.response.out.write("if(%s) { %s(%s); }" % (callback, callback, responsedata))