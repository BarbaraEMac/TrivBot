#!/usr/bin/env python

import logging
import time

from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from emailer  import Emailer
from helpers import *
from models import User, Question, Troupe, get_question
from main import URIHandler

class SendEmailHandler( URIHandler ):
    
    def get( self ):
        users = User.all()

        for u in users:
            if u.daily_email and not u.played_today:
                taskqueue.add( queue_name = 'dailyEmailQueue', 
                               url        = '/queue/dailyEmail',
                               params     = {'uuid' : u.uuid} )

class ResetPlayedFlagHandler( URIHandler ):
    
    def get( self ):
        users = User.all()
        for u in users:
            taskqueue.add( queue_name = 'playedFlagReset', 
                           url        = '/queue/playedFlagReset',
                           params     = {'uuid' : u.uuid} )

class UpdateQuestionHandler( URIHandler ):
    
    def get( self ):
        # Fetch question
        q = get_question()
        
        # And mark it as used!
        if q:
            q.state = 'used'
            q.put()

        # Get a new question
        new_q = Question.all().filter("state = ", 'unused').get()
        
        # Set the day to today!
        new_q.day   = triv_today( )
        new_q.state = 'in_use'

        # Save the new question
        new_q.put()

        if Question.all().filter('state = ', 'unused').count() <= 3:
            Emailer.outOfQuestions()

class ClearTroupeHandler( URIHandler ):

    def get( self ):
        troupes = Troupe.all()

        for t in troupes:
            if t.num_members <= 0:
                t.delete()

class MonthlyResetHandler( URIHandler ):
    
    def get( self ):
        troupes = Troupe.all()
        winners = []
        players = []

        for t in troupes:
            members = t.get_uuid_memberlist()

            for m in members:
                logging.error("XX %s %s" % (m[0], m[1]) )

            winners.append( User.get_by_uuid( members[0][1] ) )
            players.append( len(members) )
            
            if len(members) > 1:
                winners.append( User.get_by_uuid( members[1][1] ) )
                players.append( len(members) )
            
            if len(members) > 2:
                winners.append( User.get_by_uuid( members[2][1] ) )
                players.append( len(members) )
            
        Emailer.adminMonthlySummary( winners, players )

        users = User.all()

        for u in users:
            # Make sure they played this month.
            if u.get_days_played() > 0:
                taskqueue.add( queue_name = 'dailyEmailQueue', 
                               url        = '/queue/monthlySummary',
                               params     = {'uuid' : u.uuid} )


##### Call Handler #####
########################
application = webapp.WSGIApplication([
                                      ('/cron/clearTroupes', ClearTroupeHandler),
                                      ('/cron/monthlyReset', MonthlyResetHandler),
                                      ('/cron/sendEmails', SendEmailHandler),
                                      ('/cron/playedFlagReset', ResetPlayedFlagHandler),
                                      ('/cron/updateQuestion', UpdateQuestionHandler),
										], debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()    
