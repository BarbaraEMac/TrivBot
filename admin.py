#!/usr/bin/env python
import hashlib 
import logging
import os
import random
import simplejson as json 

from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users

from consts  import *
from cookies import LilCookies
from emailer import Emailer
from helpers import *
from main    import URIHandler, login_required
from models  import User, Question, Troupe, get_unapproved_question, get_approving_question, get_questions_with_submitters, get_unapproved_question_count

class AdminHandler( URIHandler ):
    
    def get( self ):
        q = get_approving_question()

        if q == None or q.question == None:
            q = get_unapproved_question()

        if q == None:
            q = Question()
            
        """
        q_submitters = get_questions_with_submitters()
        submitters   = []
        for s in q_submitters:
            if s.submitter and not s.submitter in submitters:
                submitters.append( s.submitter )
        """

        logging.info('Question: %s %s %s' % (q.question, q.category, q.answer))

        q.state = 'approving'
        q.put()

        template_values = { 
            'CSS_FILE' : 'admin',
            'JS_FILE' : '',
            'q' : q,
            'num_not_approved' : get_unapproved_question_count()
        }
        
        self.response.out.write( template.render( 'templates/admin.html', template_values ) )
    
class TestHandler ( URIHandler ):

    def get( self ):
        qwe = Question.all()
        for q in qwe:
            if hasattr(q, 'used'):
                logging.error("Deleting 1 %s" % q.question)
                delattr(q, 'used')
                delattr(q, 'offer_id')
                q.put()
            #q.state = 'used'
            #q.delete()
        
        path = os.path.join(os.path.split(__file__)[0], 'next_q.csv')
        f = open( path, 'r' )

        items = f.read().split('\n')
        logging.error("NUM QUERIOSN %d" % len(items) )

        j = qwe.count()
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
            difficulty=tmp[0],
            category=tmp[1])
            
            q.put()
            logging.error("PUTTING 1")
            j += 1
        self.response.out.write( "done" )

class TroupeHandler( URIHandler ):

    @login_required
    def get( self, user ):
        user = self.get_user()

        if user and not user.troupe:
            user.troupe = Troupe.get_or_create( 'Everyone' )
            user.put()

class UpdateUsers( URIHandler ):
    def get( self ):
        users = User.all()

        for u in users:
            u.put()
        
        self.response.out.write( "done" )

class AddQuestionHandler( URIHandler ):
    def post( self ):
        question    = self.request.get( 'question' )
        correct     = self.request.get( 'answer' )
        cat         = self.request.get( 'category' )
        diff        = self.request.get( 'difficulty' )
        incorrect_1 = self.request.get( 'incorrect_1' )
        incorrect_2 = self.request.get( 'incorrect_2' )
        incorrect_3 = self.request.get( 'incorrect_3' )
        submitter_id = self.request.get( 'submitter_uuid' )

        q = get_approving_question()
        submitter = User.get_by_uuid( submitter_id )

        random.seed( question )
        a = random.randint( 1, 4 )

        if a == 1:
            q.question = question
            q.opt_1    = correct
            q.opt_2    = incorrect_1
            q.opt_3    = incorrect_2
            q.opt_4    = incorrect_3
            q.answer   = correct
            q.state    = 'unused'
            q.category = cat
            q.difficulty = diff
            q.submitter  = submitter

        elif a == 2:
            q.question = question
            q.opt_1    = incorrect_1
            q.opt_2    = correct
            q.opt_3    = incorrect_2
            q.opt_4    = incorrect_3
            q.answer   = correct
            q.state    = 'unused'
            q.category = cat
            q.difficulty = diff
            q.submitter  = submitter
        
        elif a == 3:
            q.question = question
            q.opt_1    = incorrect_1
            q.opt_2    = incorrect_2
            q.opt_3    = correct
            q.opt_4    = incorrect_3
            q.answer   = correct
            q.state    = 'unused'
            q.category = cat
            q.difficulty = diff
            q.submitter  = submitter

        else:
            q.question = question
            q.opt_1    = incorrect_1
            q.opt_2    = incorrect_3
            q.opt_3    = incorrect_2
            q.opt_4    = correct
            q.answer   = correct
            q.state    = 'unused'
            q.category = cat
            q.difficulty = diff
            q.submitter  = submitter


        if submitter:
            q.put()
            
            old_place = submitter.get_place()
            
            submitter.add_message( 'The question you submitted was approved!<br /> You\'ve gained 3 points! Keep submitting to gain even more points!' )
            submitter.score += 3
            submitter.put()
            
            new_place = submitter.get_place()
            if new_place < old_place:
                submitter.add_message( 'You just overtook someone and scored place #%s' % new_place )

        self.redirect( '/admin' )

class MessageHandler( URIHandler ):

    def post( self ):
        uuid = self.request.get( 'uuid' )
        msg  = self.request.get( 'msg' )

        user = User.get_by_uuid( uuid )
        user.add_message( msg )

        self.redirect( '/admin' )

def main():
    application = webapp.WSGIApplication([
                                          ('/admin', AdminHandler),
                                          ('/admin/addQuestion', AddQuestionHandler),
                                          ('/admin/message', MessageHandler),
                                          ('/test', TestHandler),
                                          ('/test/users', UpdateUsers),
                                          ('/test/troupe', TroupeHandler),
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
