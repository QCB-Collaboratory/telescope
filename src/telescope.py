## standard libraries
import sys, os, io
import datetime, time

## signal processing and math
import numpy as np

## to create threads
import multiprocessing as mp

## For the web service
import tornado.ioloop
import tornado.web as web
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient
import logging

##
import configparser


## Import internal modules
from sshKernel import tlscpSSH


rootdir = './'#os.path.dirname(__file__)


class MainHandler(tornado.web.RequestHandler):
    """
    Root access
    """

    def get(self):

        self.render('pages/index.html', title="Farore's wind",
                    content = '<p>Test.</p>',
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return



class experimentHandler(tornado.web.RequestHandler):

    def get(self):

        expID        = self.get_argument('expID', '-1')
        outputStatus = self.get_argument('outputFormat', '0')


        if expID == '-1':
            content = "<p>Experiment ID not provided.</p>"

        else:
           
            ## Grabbing the current state of the output file
            connection = tlscpSSH(username)

            ## Accessing the current status
            connection.query("qstat | grep "+username)
            curStatus  = connection.returnedText
            time.sleep(0.5)

            ## Accessing the current output
            if outputStatus == '1':
                cmd = "cat "
            else:
                cmd = "tail -n 20 "
            connection.query( cmd + " telescope_test/output.dat" )
            curOutput  = connection.returnedText

            connection.close()

            ## Constructing the info to post on the web page
            header = "job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID".replace('\t',"&#9;")
            content = "<p><b>Status:</b><br />" + header + "<br />" + curStatus.replace('\t',"&#9;") + "</p>"
            content += "<p><b>Command:</b> python generate_test.py</p>"

            output2print = curOutput.replace('\n', '<br />')

            if outputStatus == '1':
                content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=0\">here</a> to see the only the last 20 lines of the output file.</p>"
                content += "<p><b>Current status of the output:</b></p>"

            else:
                content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=1\">here</a> to see the full output file.</p>"
                content += "<p><b>Latest 20 lines:</b></p>"

            content += "<blockquote>"
            content += output2print
            content += "</blockquote>"


        ## Rendering the page
        self.render('pages/index.html', title="Farore's wind",
                    content = content,
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return




class loggingHandler(tornado.web.RequestHandler):

    def initialize(self):

        self.filename = 'telescope_server.log' ### this is too hard-coded

        return


    def get(self):

        logfile    = open(self.filename).read()
        logEntries = logfile.split('\n')

        content = '<div class="page-header">' + \
                '<table class="table table-striped">' + \
                '<thead><tr><th width=100px>logger</th><th>Level</th><th>date</th><th>Message</th></tr></thead>'+ \
                '<tbody>\n'


        for entry in logEntries[-1:-200:-1]:

            if len( entry.split('--') ) == 2:
                [metadata, message] = entry.split('--')

                ## Removing access to css and js stuff
                simpleAccessCheck = "304 GET /static/css/bootstrap.css" in message or \
                   "304 GET /static/js/bootstrap.min.js" in message or \
                   "304 GET /static/css/custom.css" in message

                if not simpleAccessCheck:

                    ## Simple parser
                    mtdt_spl = metadata.split(' ')
                    loggerID = mtdt_spl[0]
                    logLevel = mtdt_spl[2]
                    logDate  = mtdt_spl[4]
                    logTime  = mtdt_spl[5]

                    ## Styling warning and errors
                    STYLE=""
                    if logLevel == "WARNING": STYLE = "style=\"color: #FA2; font-weight: bold;\""
                    if logLevel == "ERROR": STYLE = "style=\"color: #F00; font-weight: bold;\""

                    content += "<tr " + STYLE + "><td>"+loggerID+"</td><td>"+logLevel+"</td><td>"+logDate+" "+logTime[:8]+"</td><td>"+message+"</td></tr>\n"

            else:
                print( entry )

        content += '</tbody></table></div>'

        self.render(rootdir+'/pages/index.html', title="Server logs", content = content,
                    top=open(rootdir+"/pages/top.html").read(), bottom=open(rootdir+"/pages/bottom.html").read())

        return






class telescope:

    def __init__(self):
        """ This starts the server.
        """

        self.port = 4000

        ## Setting up the logging
        logging.basicConfig(filename='telescope_server.log',
                            level=logging.DEBUG,
                            format='%(name)s @ %(levelname)s # %(asctime)s -- %(message)s')


        ## Loading configuration file
        config = configparser.ConfigParser()
        config.read('config.ini')
            
            
        # Extract name of the account that will be used for log-in
        self.credential_username = config['CREDENTIALS']['USER']
            
        # If there is a password listed, get that
        if config.has_option('CREDENTIALS', 'PASS'):
            self.credentialsPASS = config['CREDENTIALS']['PASS']
        else:
            self.credentialsPASS = ''
    
    
        # Create a list of the users whose jobs we'd like to examine
          
        self.user_names = []
        for ii in range(config['MONITOR']['NUMUSERS']):
            self.user_names.append(config['MONITOR']['USER'+str(ii)])
        self.user_names




        ## Starting tornado
        handlers = [
            (r'/', MainHandler),
            (r'/logging', loggingHandler),
            (r'/experiment', experimentHandler),
        ]

        settings = dict(
            static_path = os.path.join(os.path.dirname(__file__), "pages")
            )

        application = web.Application(handlers, **settings)
        application.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()

        return




if __name__ == "__main__":
    server = telescope()
