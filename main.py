
import datetime
import time
import logging
import os
import random
import re
import model
import cgi
import calendar
from django.utils import simplejson as json

#channel api
from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class InvalidRequestException( Exception ):
    def __init__( self, msg ):
        self.message = msg

class MainPage(webapp.RequestHandler):
    """Main UI Page, renders the front page"""
    def get(self):
        token = channel.create_channel("rhokds")
        template_values = {"token":token}
        path = os.path.join(os.path.dirname(__file__), "templates/stream.html")
        self.response.out.write(template.render(path, template_values))
        
class FeedHandler(webapp.RequestHandler):
    """Feeds"""
    def get(self):
        query  = model.Message.all()
        retlist = []
        out=""
        for q in query:
            k = q.__dict__.keys()
            print q.__dict__
            r = { "handler": q.handler }
            r["text"] = q.text
            r["timestamp"] = calendar.timegm(q.timestamp.timetuple())
            if "imgpath" in k:
                r["imgpath"] = q.imgpath
            if "timestamp" in k:
                r["timestamp"] = q.timestamp
            if "lat" in k:
                r["lat"] = q.lat
            if "lon" in k:
                r["lon"] = q.lon
            if "category" in k:
                r["category"] = q.category
            retlist.append( r )

        self.response.out.write({"status":"ok", "data": retlist})
        
class PostHandler(webapp.RequestHandler):
    """A Poster Handler"""
    def post(self):      
        args = self.request.arguments()
        msg  = None
        jsu = {}
        try:
            if "handler" not in args:
                raise InvalidRequestException("`handler` field not found")
            else:
                msg = model.Message( handler = self.request.get("handler"));
                jsu["handler"] = msg.handler

            if ( "text" not in args ) and ("imgpath" not in args):
                raise InvalidRequestException("`text` and `imgpath` not found")

            if "text" in args:
                msg.text = self.request.get("text")
                jsu["text"] = msg.text
            if "imgpath" in args:
                msg.imgpath = self.request.get("imgpath")
                jsu["imgpath"] = msg.imgpath
            try:
                msg.timestamp = datetime.datetime.fromtimestamp( long( self.request.get( "timestamp")))
                jsu["timestamp"] = long( self.request.get( "timestamp" ) )
            except ValueError:
                msg.timestamp = datetime.datetime.utcnow()
                jsu["timestamp"] = calendar.timegm(datetime.datetime.utcnow().timetuple())

            if ("lat" in args) and ("lon" in args):
                msg.loc = db.GeoPt( float( self.request.get("lat")),
                                    float( self.request.get("lon")))
                jsu["lat"] = float( self.request.get("lat") )
                jsu["lon"] = float( self.request.get("lon") )
            if "category" in args:
                msg.category = db.Category( self.request.get("category") )
                jsu["category"] = msg.category

            msg.put()

            channel.send_message("rhokds", json.dumps(jsu))

            print  msg.handler,": ", msg.text

            self.response.headers["Content-Type"]="application/json"
            
            self.response.out.write(json.dumps({"status":"ok"}))

        except InvalidRequestException as ex:
            self.response.headers["Content-Type"]="application/json"
            self.response.out.write(json.dumps({"status":"failed", "message":ex.message}))
        #except:
         #   self.response.headers["Content-Type"]="application/json"
          #  self.response.out.write(json.dumps({"status":"failed", "message":"invalid names"}))
        
                    
application=webapp.WSGIApplication([
        ('/', MainPage),
        ('/post', PostHandler),
        ('/feed', FeedHandler)
        ])

def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
