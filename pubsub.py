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
from pshb import HubSubscriber, ContentParser

class PubsubHandler(webapp.RequestHandler):
  def get(self):
    '''
    We handle all requests to subscribe to an activity here
    '''
    mode = self.request.get("hub.mode")
    challenge = self.request.get("hub.challenge")
    verify_token = self.request.get("hub.verify_token")
    
    if mode == "subscribe":
      if verify_token == settings.SECRET_TOKEN:
        logging.info("Confirmed Sub")
        self.response.out.write(challenge)
      else:
        logging.info("Not found")
        self.response.set_status(404)
      
      return
    else:
      # Update the cache of data.
      pass
      
  def post(self):
    '''
    New content has been pushed to the hub.  Invalidate the cache, and other 
    things
    '''
    logging.info(self.request)
    
    # data is delievered by xml so involke the power of feedparser
    content = ContentParser(self.request.body)
    article = content.extractPosts()[0].getFeedParserEntry()
    
    id = article["id"]
    #username = article["username"]
    #title = article["title"]
    
    activity = model.Activity.Get({"id" : id})
    if activity:
      activity.delete()
    