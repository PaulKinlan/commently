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
from google.appengine.api import tasks

from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

import simplejson
import settings
import decorators
import logging
import urllib
import os
import model
from pshb import HubSubscriber

class PubsubSubscribeHandler(webapp.RequestHandler):
  def post(self):
    '''
    We handle all requests to subscribe to an activity here
    '''
    id = self.request.get("id")
    username = self.request.get("username")
    title = self.request.get("title")
    
    url = settings.ACTIVITY_URL % (username, id)
    hub = settings.DEFAULT_HUB
    
    subscriber = HubSubscriber()
    subscriber.subscribe(url, hub, settings.CALLBACK_URL)
