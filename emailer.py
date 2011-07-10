#!/usr/bin/env python
import logging

from datetime import datetime, date, timedelta
from google.appengine.api import mail
from google.appengine.api.mail import EmailMessage

from helpers import *
from models import Question

###################
#### Addresses ####
###################

from_addr = 'daily.triv.bot@gmail.com' # must be registered with app engine account

#####################
#### Email Class ####
#####################
class Emailer():
    
    @staticmethod
    def invite( addr, user ):
        to_addr = addr
        subject = '[TrivBot] You\'ve Been Challenged!'
        body    = ''' <html> <head> <style type="text/css"> body {background-image: url("http://www.trivbot.com/images/question_grey3.png"); background-repeat: no-repeat; background-attachment: fixed; background-position: bottom right; font-family: monaco, monospace; font-size: 1.1em; background-color: black; color: yellow; border: 5px solid #0e53a7; border-radius: 20px; } </style> </head> <body > <div> <div style="width: 100&#37;;"><a href="http://www.trivbot.com"><img height="100px" src="http://www.trivbot.com/images/logo_bot5.png" alt="TrivBot"></a></img></div> <div style="width: 100&#37;;"><h1 style="font-size: 2.5em; padding-top: 14px; padding-left: 20px;"> Hi! </h1></div> </div> <div> <p style="padding-left: 20px; padding-right: 20px"> %s %s has thrown down the gauntlet and issued you a <b>challenge</b>.  See, %s thinks s/he is smarter than you. It's time to prove her/him wrong, smarty pants! </p> <p style="padding-left: 20px; padding-right: 20px"> Join %s on <a href="http://www.trivbot.com"><img height="25px" src="http://www.trivbot.com/images/logo_no.png" alt="TrivBot"></img></a> and show her/him who's boss! <a href="http://www.trivbot.com"><img height="25px" src="http://www.trivbot.com/images/logo_no.png" alt="TrivBot"></img></a>  is a daily trivia challenge mailed straight to your inbox every morning. </p> <h2 style="font-size: 1.8em; padding-left: 20px">The Stakes?</h2> <p style="padding-left: 20px; padding-right: 20px"> You can win real, cold, hard cash just by playing <a href="http://www.trivbot.com"><img height="25px" src="http://www.trivbot.com/images/logo_no.png" alt="TrivBot"></img></a>  daily against your friends and co-workers.  Wouldn't you like to earn both %s's money and the title of <b> Supreme Trivia Master</b>? </p> <p style="padding-left: 20px; padding-right: 20px"> Visit <a href="http://www.trivbot.com"><img height="25px" src="http://www.trivbot.com/images/logo_no.png" alt="TrivBot"></img></a> today to start dominating the competition! Join %s's troupe, "%s", and begin your battle.</p> <p style="padding-left: 20px; padding-right: 20px"> -- <img height="60px" src="http://www.trivbot.com/images/logo_bot5.png" alt="TrivBot"></img> Team</p> </div> </body> </html>''' % (user.first_name, user.last_name, user.first_name, user.first_name, user.first_name, user.first_name, user.troupe.name)     

        Emailer.send_email( from_addr, to_addr, subject, body )

    @staticmethod
    def feedback ( question, correct, incorrect_1, incorrect_2, incorrect_3, user ):
        to_addr = from_addr
        subject = '[TrivBot] Question Submittal'
        body    = """ <p>From: %s %s (%s)</p><p>Q: %s</p><p>C: %s</p><p>In1: %s</p><p>In2: %s</p><p>In3: %s</p>""" %(user.first_name, user.last_name, user.email, question, correct, incorrect_1,
        incorrect_2, incorrect_3)

        logging.info('body: %s' % body)
        
        Emailer.send_email( from_addr, to_addr, subject, body )

    @staticmethod
    def dailyEmail( user ):
        question = Question.all().filter('day = ', triv_today()).get()
        #logging.error('question %s %s %s' % (question.question, question.category, question.difficulty))
        to_addr  = user.email
        subject  = '[TrivBot] Today\'s Question'
        body     = """ <html> <head><style type="text/css"> body {background-image: url("http://www.trivbot.com/images/question_grey3.png");
        background-repeat: no-repeat; background-attachment: fixed; background-position: bottom right; font-family: monaco, monospace; font-size: 1.1em;
        background-color: black; color: yellow; border: 5px solid #0e53a7; border-radius: 20px;}</style></head><body><center><div><div><h2>Morning %s
        %s!</h2></div> </div> <div> <p>Here is today's (%s) category:</p> <h1>%s</h1> <p>and difficulty: <h1>%s / 3.</h1></p> <p> Visit <a
        href="http://www.trivbot.com">www.trivbot.com</a> today to increase your score!</p><p>Remember: if you PASS, you still get points!</p><p> -- TrivBot Team</p> </div><div><a href="http://www.trivbot.com"><img alt="TrivBot" height="100px" src="http://www.trivbot.com/images/logo_bot5.png"></a></img><p>To stop receiving these emails, uncheck the 'Daily Email' box on the Account page.</p></div> </center></body> </html> 
        """ % ( user.first_name, user.last_name, datetime.date( datetime.today() ).strftime( '%A %B %d, %Y' ), question.category, question.difficulty )
        
        #logging.error(body)

        Emailer.send_email( from_addr, to_addr, subject, body )

    @staticmethod
    def outOfQuestions( ):
        to_addr = from_addr
        subject = '[TrivBot] OUT of Questions'
        body    = 'Running out'

        Emailer.send_email( from_addr, to_addr, subject, body )

    @staticmethod
    def monthlySummary( user ):
        yesterday = date.today() - timedelta(1)
        
        to_addr = user.email
        subject = '[TrivBot] Monthly Summary!'
        body    = """<html> <head> <style type="text/css"> body {background-image: url("http://www.trivbot.com/images/question_grey3.png"); background-repeat: no-repeat;
        background-attachment: fixed; background-position: bottom right; font-family: monaco, monospace; font-size: 1.1em; background-color: black; color: yellow; border: 5px solid #0e53a7;
        border-radius: 20px;} </style> </head> <body> <center> <div> <h2> Hi %s %s!</h2> </div> <div> <p>Well, it's the end of <em>%s</em>, so it's time to wrap up another month of trivia! Here are
        your stats:</p> <p>Number of Days Played: %d</p> <p>Number of Correct Answers: %d</p> <p>Number of Incorrect Answers: %d</p> <p>Number of Passes: %d</p> <h2>Overall, you placed #%s within
        Troupe "%s"!</h2> <p>Congratulations! Hope to see you again next month!</p> <p>NOTE: Unfortunately due to a small bug, you will have to resubmit your name information when you login
        next. I'm actively working on determining the cause of this bug. Sorry for the inconvenient additional keystrokes!</p> <p> -- TrivBot Team</p> </div> <div> <a href="http://www.trivbot.com"> <img alt="TrivBot" height="100px"
        src="http://www.trivbot.com/images/logo_bot5.png"> </a> </img> </div> </center> </body> </html> """ % (user.first_name, user.last_name, yesterday.strftime( '%B %Y' ), user.get_days_played(), user.num_correct, user.num_wrong, user.num_pass, user.get_place(), user.troupe.name)
        
        logging.error(body)

        Emailer.send_email( from_addr, to_addr, subject, body )


    @staticmethod
    def adminMonthlySummary( winners, players ):
        to_addr = from_addr
        subject = '[TrivBot] Monthly Winners'
        body    = '<html><head></head><body>'

        i = 0
        for w in winners:
            s = '<p>Troupe: %s Winner: %s %s (%s) Score: %d Num Players: %d</p>\n' % ( w.troupe.name, w.first_name, w.last_name, w.email, w.score, players[i] )
            body += s
            i += 1

        body += '</body></html>'
        logging.error(body)

        Emailer.send_email( from_addr, to_addr, subject, body )


#####################################
#####################################
#####################################

    @staticmethod
    def send_email( from_addr, to_addr, subject, body ):

        if not is_good_email( from_addr ):
            logging.warning('send_email(): From address %s is malformed.' % from_addr )
        
        if not is_good_email( to_addr ):
            logging.warning('send_email(): To address %s is malformed.' % to_addr )

        e = EmailMessage(sender=from_addr, to=to_addr, subject=subject, html=body)
        e.send()
