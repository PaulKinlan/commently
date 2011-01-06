from google.appengine.ext import db


class ActivityStore(db.Model):
  activity_id = db.StringProperty()