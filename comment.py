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
from buzzprocess import BuzzProcess

class CommentHandler(webapp.RequestHandler):
  def buildArgsDict(self):
    args = self.request.arguments()
    
    arguments = {}
    
    for arg in args:
      if arg == "callback":
        continue
        
      arguments[str(arg)] = urllib.unquote(self.request.get(arg))
      
    return arguments
  
  def getActivity(self, *args, **kwargs):
    activity = {}
    
    process = BuzzProcess()
    
    activity = process.FindActivity(**kwargs)
    
    return activity

class JSCommentHandler(CommentHandler):
  @decorators.cors
  def get(self, extension = "js"):
    output = "{}"
    callback = self.request.get("callback")
    dictArgs = self.buildArgsDict()
    
    activity = self.getActivity(**dictArgs)
   
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
    
    dictArgs = self.buildArgsDict()
    
    logging.info("ARGS %s" % dictArgs)
    
    activity = self.getActivity(**dictArgs)
    logging.info("Activity %s" % activity)
    
    path = os.path.join(os.path.dirname(__file__), "templates" ,'comments.tmpl')
    output = template.render(path, activity)
    
    self.response.headers["Content-Type"] = "text/html"
    self.response.out.write(output)