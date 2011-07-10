import logging
import random
import time

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from emailer import Emailer
from helpers import *
from models  import User

#### Task Queue Functions ####
##############################
class DailyEmailSender( webapp.RequestHandler ):
    
    def post( self ):
        uuid = self.request.get( 'uuid' ) 
        u    = User.get_by_uuid( uuid )

        random.seed( uuid )

        time.sleep( random.randint(0, 29) )

        Emailer.dailyEmail( u )

class MonthlySummarySender( webapp.RequestHandler ):
    
    def post( self ):
        uuid = self.request.get( 'uuid' ) 
        u    = User.get_by_uuid( uuid )

        random.seed( uuid )

        time.sleep( random.randint(0, 29) )

        Emailer.monthlySummary( u )
       
        u.reset()


class ResetPlayedFlag( webapp.RequestHandler ):
    
    def post( self ):
        uuid = self.request.get( 'uuid' ) 
        u    = User.get_by_uuid( uuid )

        u.played_today = False
        u.save()

application = webapp.WSGIApplication([
                                      ('/queue/dailyEmail', DailyEmailSender),
                                      ('/queue/monthlySummary', MonthlySummarySender),
                                      ('/queue/playedFlagReset', ResetPlayedFlag)
                                        ], debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()    

