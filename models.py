import os
import logging

from datetime import datetime

from google.appengine.ext import db
from google.appengine.api import users

from consts import *

class User( db.Model ):
    uuid         = db.StringProperty( default = '' )
    first_name   = db.StringProperty( default = '' )
    last_name    = db.StringProperty( default = '' )
    email        = db.StringProperty( default = '' )
    daily_email  = db.BooleanProperty( default = True )
    joined       = db.DateTimeProperty( auto_now_add = True )
    last_played  = db.DateTimeProperty()
    played_today = db.BooleanProperty( default = False )
    troupe       = db.ReferenceProperty()
    score        = db.IntegerProperty( default = 0 )
    num_correct  = db.IntegerProperty( default = 0 )
    num_wrong    = db.IntegerProperty( default = 0 )
    num_pass     = db.IntegerProperty( default = 0 )
    messages     = db.StringListProperty ( default = '' )
    place        = db.IntegerProperty( default = 1 )

    @staticmethod
    def get_by_uuid( uuid ):
        return User.all().filter('uuid = ', uuid ).get()

    @staticmethod
    def get_or_create_by_uid( uuid ):
        user = User.get_by_uuid( uuid )
        
        # If not User, create and store it.
        if user == None:
            Troupe.get_or_create( 'Everyone' )
            
            user        = User ()
            user.uuid   = uuid
            user.troupe = Troupe.join_troupe( 'Everyone', user )
            user.put()
        return user

    def update_score( self, question, ans ):
        prev_place = self.get_place()
        
        s = 0
        if ans == PASS:
            s = 1
            self.num_pass += 1
            question.num_pass += 1
        elif question.is_correct( ans ):
            s += 2
            self.num_correct += 1
            question.num_correct += 1
        else:
            s = -1
            self.num_wrong += 1
            question.num_wrong += 1
        
        self.score += s
        self.put()

        new_place = self.get_place()

        if new_place < prev_place:
            self.add_message('You just overtook someone and scored place #%s' % new_place)

        question.put()

        return s

    def switch_troupe( self, new_troupe_name ):
        self.troupe.leave_troupe( )

        self.troupe = Troupe.join_troupe( new_troupe_name, self )

        self.put( )

    def get_troupe_mates( self ):
        return self.troupe.get_memberlist( )

    def get_days_played( self ):
        return self.num_correct + self.num_wrong + self.num_pass

    def reset( self ):
        self.score       = 0
        self.num_correct = 0
        self.num_wrong   = 0
        self.num_pass    = 0
        self.put()

    def get_place( self ):
        mates = self.get_troupe_mates()

        for m in mates:
            if self.first_name in m and self.last_name[0] in m:
                return m.split('.')[0]

    def add_message( self, msg ):
        self.messages.append( '%s: %s' % (datetime.date( datetime.today() ) .strftime( '%a %B %d' ), msg) )
        self.put()

# end User

class Question( db.Model ):
    question    = db.StringProperty()
    opt_1       = db.StringProperty()
    opt_2       = db.StringProperty()
    opt_3       = db.StringProperty()
    opt_4       = db.StringProperty()
    answer      = db.StringProperty()
    category    = db.StringProperty()
    difficulty  = db.StringProperty()
    state       = db.StringProperty( default = 'unused' )
    day         = db.DateProperty( default=None )
    num_correct = db.IntegerProperty( default = 0 )
    num_wrong   = db.IntegerProperty( default = 0 )
    num_pass    = db.IntegerProperty( default = 0 )
    submitter   = db.ReferenceProperty( User, default = None )
    
    def is_correct( self, ans ):
        if self.answer == ans:
            return True

        return False

    def incr_correct( self ):
        self.num_correct += 1
        self.put()

    def incr_wrong( self ):
        self.num_wrong += 1
        self.put()

    def incr_pass( self ):
        self.num_pass += 1
        self.put()

def get_question( ):
    q = Question.all().filter('state = ', 'in_use').get()
    return q

def get_unapproved_question( ):
    q = Question.all().filter('state = ', 'not_approved').get()
    return q

def get_unapproved_question_count( ):
    q = Question.all().filter('state = ', 'not_approved').count()
    return q 

def get_approving_question( ):    
    q = Question.all().filter('state = ', 'approving').get()
    return q

def get_questions_with_submitters( ):    
    q = Question.all().filter('submitter != ', 'None')
    return q

# end Question


class Troupe( db.Model ):
    name        = db.StringProperty( )
    num_members = db.IntegerProperty( default = 0 )
    started     = db.DateProperty( auto_now_add = True )

    def get_members( name ):
        return User.all().filter( 'troupe =', self )
    
    @staticmethod
    def create_troupe( name ):
        
        troupe = Troupe( key_name = name.capitalize(), name = name.capitalize() )
        troupe.put()
        
        return troupe

    @staticmethod
    def get_troupe( name ):
        return Troupe.get_by_key_name( name )

    @staticmethod
    def get_or_create( name ):
        troupe = Troupe.get_troupe( name )

        if troupe == None:
            troupe = Troupe.create_troupe( name )
        
        return troupe
    
    def leave_troupe( self ):
        self.num_members -= 1
        self.put()

    @staticmethod
    def join_troupe( troupe_name, user ):
        new_troupe = Troupe.get_or_create( troupe_name )

        new_troupe.num_members += 1
        new_troupe.put()

        return new_troupe

    def get_memberlist( self ):
        users = User.all()
        tmp   = []
        logging.info("COUNT %d" % users.count())

        # Build list of everyone in this troupe
        i = 0
        for u in users:
            if u.troupe.name == self.name:
                if u.first_name and u.last_name and u.email:
                    tmp.append( (u.score, u.first_name, u.last_name[0]) )
                    logging.info( "%s" % str(tmp[i]) )
                    i += 1
        
        # Sort list
        tmp = sorted( tmp, key=lambda x: -x[0] ) # Sort in desc order by score

        # Construct list to return
        ret = []
        i   = 1
        for t in tmp:
            ret.append( "%d. %s %s." % (i, t[1], t[2]) )
            i += 1

        return ret

    def get_uuid_memberlist( self ):
        users = User.all()
        tmp = []
        logging.info("COUNT %d" % users.count())

        # Build list of everyone in this troupe
        i = 0
        for u in users:
            if u.troupe.name == self.name:
                if u.first_name and u.last_name and u.email:
                    tmp.append( (u.score, u.uuid) )
                    logging.info( "%s" % str(tmp[i]) )
                    i += 1
        
        # Sort list
        tmp = sorted( tmp, key=lambda x: -x[0] ) # Sort in desc order by score

        logging.error("ORDER")
        for t in tmp:
            logging.error( "%s %s" % (t[0], t[1]) )

        return tmp

        
# end Troupe
