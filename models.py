import os
import logging

from datetime import datetime

from google.appengine.ext import db
from google.appengine.api import users

from consts import *

class User( db.Model ):
    google_user  = db.UserProperty()
    first_name   = db.StringProperty( default = '' )
    last_name    = db.StringProperty( default = '' )
    email        = db.StringProperty( default = '' )
    daily_email  = db.BooleanProperty( default = True )
    last_played  = db.DateProperty()
    troupe       = db.ReferenceProperty()
    score        = db.IntegerProperty( default = 0 )

    @staticmethod
    def get_by_google_user(g_user):
        return User.all().filter('google_user = ', g_user).get()

    @staticmethod
    def get_or_create( g_user ):
        user = User.get_by_google_user( g_user )
            
        # If not User, create and store it.
        if user == None:
            Troupe.get_or_create( 'Everyone' )
            
            user = User ()
            user.google_user = g_user
            user.email       = g_user.email()
            user.troupe      = Troupe.join_troupe( 'Everyone', user )
            user.put()

        return user

    def update_score( self, question, ans ):
        s = 0
        if ans == PASS:
            s = 1
        elif question.is_correct( ans ):
            s += 2
        else:
            s = -1
        
        self.score += s
        self.put()

        return s

    def switch_troupe( self, new_troupe_name ):
        self.troupe.leave_troupe( )

        self.troupe = Troupe.join_troupe( new_troupe_name, self )

        self.put( )

    def get_troupe_mates( self ):
        return self.troupe.get_memberlist( )

# end User

class Question( db.Model ):
    question   = db.StringProperty()
    opt_1      = db.StringProperty()
    opt_2      = db.StringProperty()
    opt_3      = db.StringProperty()
    opt_4      = db.StringProperty()
    answer     = db.StringProperty()
    category   = db.StringProperty()
    difficulty = db.StringProperty()
    offer_id   = db.StringProperty()
    used       = db.BooleanProperty( default=False )
    day        = db.DateProperty( default=None )

    def is_correct( self, ans ):
        if self.answer == ans:
            return True

        return False

# end Question


class Troupe( db.Model ):
    name        = db.StringProperty( )
    num_members = db.IntegerProperty( default = 0 )
    started     = db.DateProperty( auto_now_add = True )

    @staticmethod
    def create_troupe( name ):
        troupe = Troupe( key_name = name, name = name )
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
        tmp = []
        logging.info("COUNT %d" % users.count())

        # Build list of everyone in this troupe
        i = 0
        for u in users:
            if u.troupe.name == self.name:
                if u.first_name and u.last_name:
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
# end Troupe
