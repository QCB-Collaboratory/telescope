## standard libraries
import sys, os, io
import datetime, time

## to create parallel processes
import multiprocessing as mp
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager

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
from jobStatusMonitor import jobStatusMonitor
from MainHandler import MainHandler
from experimentHandler import experimentHandler
import utils


rootdir = './'#os.path.dirname(__file__)




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





def monitorLoop( queueMonitor ):
    """
    Loop that keeps updating the monitor in constant
    intervals of time.
    """

    logger = logging.getLogger(__name__)

    while 1:

        logger.info('Queue monitor running...')

        queueMonitor.checkQstat()

        # sleeping between each call
        logger.info('Queue monitor sleeping...')
        time.sleep( queueMonitor.getMonitoringInterval() )

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
        logger = logging.getLogger(__name__)
        logger.info('Logging setup done.')


        ## Loading configuration file
        config = configparser.ConfigParser()
        config.read('config.ini')
        logger.info('Configurations read succesfully.')


        # Extract name of the account that will be used for log-in
        self.credential_username = config['CREDENTIALS']['USER']

        # If there is a password listed, get that
        if config.has_option('CREDENTIALS', 'PASS'):
            self.credential_password = config['CREDENTIALS']['PASS']
        else:
            self.credential_password = ''

        logger.info('Credentials parsed.')

        # Create a list of the users whose jobs we'd like to examine
        self.user_names = []
        if config.has_option('MONITOR', 'NUMUSERS') and ( config['MONITOR']['NUMUSERS'] > 0 ):
            for ii in range(int(config['MONITOR']['NUMUSERS'])):
                self.user_names.append(config['MONITOR']['USER'+str(ii)])
        else:
            self.user_names.append( self.credential_username )

        logger.info('Monitored users parsed.')


        ## Starting monitor jobs

        # Creating a monitor object
        BaseManager.register('jobStatusMonitor', jobStatusMonitor)
        manager = BaseManager()
        manager.start()
        self.queueMonitor = manager.jobStatusMonitor( self.credential_username,
                                                        self.credential_password,
                                                        self.user_names )
        # Kicking the monitor job
        monitorLoop_process = Process( target=monitorLoop, args=[ self.queueMonitor ])
        monitorLoop_process.start()


        logger.info('Parallel status monitor started.')

        ## Starting tornado

        # Defining argument dictionary
        handlerArguments = { 'credentialUsername' : self.credential_username,
                                'credentialPass'     : self.credential_password,
                                'setUsername'        : self.user_names,
                                'queueMonitor'       : self.queueMonitor }

        # Setting up handlers
        handlers = [
            (r'/', MainHandler, handlerArguments),
            (r'/logging', loggingHandler),
            (r'/experiment', experimentHandler, handlerArguments),
        ]

        # General settings
        settings = dict(
            static_path = os.path.join(os.path.dirname(__file__), "pages")
            )

        logger.info('Tornado setup done.')

        # Starting tornado server loop
        application = web.Application(handlers, **settings)
        application.listen(self.port)

        logger.info('About to start tornado loop...')
        tornado.ioloop.IOLoop.instance().start()

        return




if __name__ == "__main__":
    server = telescope()
