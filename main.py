#!/usr/bin/env python

import logging
import os
import random

from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users

from consts import *
from emailer import Emailer
from helpers import *
from models import User, Question, Troupe

####################################################################################
# Decorators
####################################################################################
def login_required( fn ):
    def check( self ):
        user = self.get_user( )
        if user:
            fn( self, user )
        else:
            # Go log in
            self.redirect( users.create_login_url( '/willet' ) )
            return
    
    return check

def name_required( fn ):
    def check( self, user ):
        if user.first_name == '' or user.last_name == '':
            self.redirect( '/account' )
            return
        else:
            fn( self, user )
    return check
    
def once_per_day( fn ):
    def check( self, user ):
        if user.last_played == triv_today():
            self.redirect( '/result' )
            return
        else:
            fn( self, user )
    return check

####################################################################################
# Handlers
####################################################################################
class URIHandler( webapp.RequestHandler ):

    def __init__(self):
        # For simple caching purposes. Do not directly access this. Use self.get_user() instead.
        self.user     = None

    def get_user(self):
        if self.user:
            return self.user

        # Get the Google session (not from the db)
        google_user = users.get_current_user()

        if google_user:
            self.user = User.get_or_create( google_user )

        return self.user
    
    def get_question( self ):
        q = Question.all().filter('day = ', triv_today()).get()
        return q

    def render_page(self, template_file_name, content_template_values):
        """This re-renders the full page with the specified template."""

        main_path = os.path.join('templates/index.html')
        content_path = os.path.join('templates/' + template_file_name )

        user = self.get_user()

        content_values = {
            'user' : user
        }
        merged_content_values = dict(content_values)
        merged_content_values.update(content_template_values)

        content = template.render( content_path, merged_content_values )

        template_values = {
            'CONTENT': content,
            'LOGOUT_URL' : users.create_logout_url( '/' ),
            'user' : user
        }
        merged_values = dict(template_values)
        merged_values.update(content_template_values)

        return template.render(main_path, merged_values)

#########
## Shows
#########
class ShowAccountHandler( URIHandler ):
    
    @login_required
    def get( self, user ):
        
        if user.first_name == '' or user.last_name == '':
            html_page    = 'first_account.html'
            troupe_mates = []
        else:
            html_page    = 'account.html'
            troupe_mates = user.get_troupe_mates ()
            while len(troupe_mates) <= 5:
                troupe_mates.append( '%d. -' % (len(troupe_mates) + 1) )

        logging.info("got %d" % len(troupe_mates))
        
        template_values = { 
            'CSS_FILE' : 'account',
            'JS_FILE' : 'account',
            'daily_email' : user.daily_email,
            'troupe_mates' : troupe_mates[0:5], # Top 5 people
        }

        self.response.out.write( self.render_page( html_page, template_values ) )

class ShowAboutHandler( URIHandler ):
    
    @login_required
    def get( self, user ):

        template_values = {
            'CSS_FILE' : 'about',
        }

        self.response.out.write( self.render_page( 'about.html', template_values ) )

class ShowQuestionHandler( URIHandler ):
    
    @login_required
    @name_required
    @once_per_day
    def get( self, user ):
        id = self.request.get( 'id' )
        q  = self.get_question()

        if q.offer_id != id:
            self.redirect( '/willet' )

        template_values = {
            'JS_FILE' : 'question',
            'CSS_FILE' : 'question',
            'TODAY' : datetime.date( datetime.today() ) .strftime( '%A %B %d, %Y' ),
            'PASS' : PASS,
            'q' : q
        }

        self.response.out.write( self.render_page( 'question.html', template_values ) )

class ShowLandingHandler( webapp.RequestHandler ):
    
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/landing.html')
        template_values = {
            'LOGIN_URL' : users.create_login_url( '/willet' ),
        }

        self.response.out.write( template.render( path, template_values ) )

class ShowWilletHandler( URIHandler ):
    
    @login_required
    @name_required
    @once_per_day
    def get( self, user ):
        q = self.get_question( )

        template_values = {
            'CSS_FILE' : 'willet',
            'offer_id' : q.offer_id
        }

        self.response.out.write( self.render_page( 'willet.html', template_values ) )

class ShowResultHandler( URIHandler ):

    @login_required
    @name_required
    def get( self, user ):
        if user.last_played != triv_today():
            self.redirect( '/willet' )
            return

        score = self.request.get( 'score' )
        if not score:
            score = 0

        already_played = False
        if not (score == '1' or score == '2' or score == '-1'):
            if user.last_played == triv_today():
                already_played = True
    
        template_values = {
            'CSS_FILE' : 'result',
            'q_score' : int(score),
            'score' : user.score,
            'question' : self.get_question().question,
            'answer' : self.get_question().answer,
            'already_played' : already_played
        }

        self.response.out.write( self.render_page( 'result.html', template_values ) )

#######
## Do's
#######
class DoInviteHandler( URIHandler ):

    @login_required
    def post( self, user ):
        email = self.request.get( 'email' )
        
        if is_good_email( email ):
            Emailer.invite( email, user )
        else:
            self.response.set_status( 400 )
        
class DoUpdateAccountHandler( URIHandler ):
    
    @login_required
    def post( self, user ):

        first_name  = self.request.get( 'first_name' )
        last_name   = self.request.get( 'last_name' )
        email       = self.request.get( 'email' )
        daily_email = self.request.get( 'daily_email' )

        if is_good_name( first_name ):
            user.first_name = first_name.capitalize()
        else:
            self.response.set_status( 400 )
            return
        
        if is_good_name( last_name ):
            user.last_name  = last_name.capitalize()
        else:
            self.response.set_status( 401 )
            return

        if is_good_email( email ):
            user.email      = email
        else:
            self.response.set_status( 402 )
            return

        if daily_email == 'first':
            user.daily_email = True
            user.put()
            self.response.set_status( 403 )
        else:
            user.daily_email = True if daily_email == 'on' else False
            user.put()
            self.redirect( '/account' )

class DoUpdateTroupeHandler( URIHandler ):
    
    @login_required
    def post( self, user ):
        
        troupe_name = self.request.get( 'troupe_name' )

        if is_good_name( troupe_name ):
            user.switch_troupe( troupe_name )
        else:
            self.response.set_status( 400 )
        
        self.redirect( '/account' )

class DoSubmitFeedbackHandler( URIHandler ):
    
    @login_required
    def post( self, user ):
        feedback = self.request.get( 'feedback' )

        Emailer.feedback ( feedback, user )

        self.redirect( '/about' )

class DoAnswerQuestionHandler( URIHandler ):

    @login_required
    @name_required
    @once_per_day
    def post( self, user ):
        # Grab the user's answer
        ans = self.request.get( 'q1' )

        # Grab today's question
        question = self.get_question( )
    
        # Check if the user is correct:
        score = user.update_score( question, ans )

        # Update time
        user.last_played = triv_today()
        user.put()

        # Go to Results screen
        self.redirect( '/result?score=%s' % score )

class TestHandler ( URIHandler ):

    @login_required
    @name_required
    def get( self, user ):
        qwe = Question.all()
        for q in qwe:
            logging.error("Deleting 1 %s" % q.question)
            q.delete()

        path = os.path.join(os.path.split(__file__)[0], 'q.csv')
        f = open( path, 'r' )

        items = f.read().split('\n')
        logging.error("NUM QUERIOSN %d" % len(items) )

        j = 0#qwe.count()
        for i in items:
            if len(i) == 0:
                break

            logging.error("LINE: %s" % i)
            tmp = i.split(',')
            
            random.seed( str(j) )
            a = random.randint( 3, 6 )
            b = random.randint( 3, 6 )
            while b == a:
                b = random.randint( 3, 6 )
            c = random.randint( 3, 6 )
            while c == a or c == b:
                c = random.randint( 3, 6 )
            d = random.randint( 3, 6 )
            while d == a or d == b or d == c:
                d = random.randint( 3, 6 )
            
            q = Question( key_name=str(j), 
            question=tmp[2], 
            opt_1=tmp[a], 
            opt_2=tmp[b], 
            opt_3=tmp[c], 
            opt_4=tmp[d], 
            answer=tmp[6], 
            offer_id=tmp[7],
            difficulty=tmp[0],
            category=tmp[1])
            
            q.put()
            logging.error("PUTTING 1")
            j += 1

        self.response.out.write( "done" )

class PurchaseHandler( URIHandler ):

    @login_required
    @name_required
    def get( self, user ):
        q = self.get_question()

        self.redirect( '/question?id=%s' % q.offer_id )
        return

class TroupeHandler( URIHandler ):

    @login_required
    @name_required
    def get( self, user ):
        user = self.get_user()

        if user and not user.troupe:
            user.troupe = Troupe.get_or_create( 'Everyone' )
            user.put()


def main():
    application = webapp.WSGIApplication([
                                          ('/about', ShowAboutHandler),
                                          ('/account', ShowAccountHandler),
                                          ('/answerQuestion', DoAnswerQuestionHandler),
                                          ('/invite', DoInviteHandler),
                                          ('/question', ShowQuestionHandler),
                                          ('/result', ShowResultHandler),
                                          ('/purchase', PurchaseHandler),
                                          ('/submitFeedback', DoSubmitFeedbackHandler),
                                          ('/test', TestHandler),
                                          ('/test/troupe', TroupeHandler),
                                          ('/updateAccount', DoUpdateAccountHandler),
                                          ('/updateTroupe', DoUpdateTroupeHandler),
                                          ('/willet', ShowWilletHandler),
                                          ('/.*', ShowLandingHandler),
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
