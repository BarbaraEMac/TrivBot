#!/usr/bin/env python

import logging
import time

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from emailer  import Emailer
from helpers import *
from models import User, Question, Troupe
from main import URIHandler

class SendEmailHandler( URIHandler ):
    
    def get( self ):
        users = User.all()

        for u in users:
            if u.daily_email:
                time.sleep(10)
                Emailer.dailyEmail( u )

class UpdateQuestionHandler( URIHandler ):
    
    def get( self ):
        # Fetch question
        q = self.get_question()
        
        # And mark it as used!
        if q:
            q.used = True
            q.day  = None
            q.put()

        # Get a new question
        new_q = Question.all().filter("used = ", False).get()
        
        # Set the day to today!
        new_q.day = triv_today()

        # Save the new question
        new_q.put()

        if Question.all().filter('used = ', False).count() <= 3:
            Emailer.outOfQuestions()

class ClearTroupeHandler( URIHandler ):

    def get( self ):
        troupes = Troupe.all()

        for t in troupes:
            if t.num_members <= 0:
                t.delete()


##### Call Handler #####
########################
application = webapp.WSGIApplication([
                                      ('/cron/clearTroupes', ClearTroupeHandler),
                                      ('/cron/sendEmails', SendEmailHandler),
                                      ('/cron/updateQuestion', UpdateQuestionHandler),
										], debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()    
