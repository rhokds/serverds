
from google.appengine.ext import db

class User( db.Model ):
    handler = db.StringProperty(required=True)
    full_name = db.StringProperty(required=True)
    twitter_handler = db.StringProperty(required=False)
    twitter_access_token = db.StringProperty(required=False)

class Message( db.Model ):
    handler = db.StringProperty(required=True)
    text = db.StringProperty(required=False)
    imgpath = db.StringProperty(required=False)
    timestamp = db.DateTimeProperty(required=False)
    loc = db.GeoPtProperty(required=False)
    category = db.CategoryProperty(required=False)
