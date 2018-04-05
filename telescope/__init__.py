## standard libraries
import sys, os, io, base64
import datetime, time
import signal
import webbrowser
import configparser

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

## Import internal modules
from telescope.server import SGEServerInterface
from telescope.sshKernel import tlscpSSH
from telescope.jobStatusMonitor import jobStatusMonitor
from telescope.MainHandler import MainHandler
from telescope.experimentHandler import experimentHandler
from telescope.UserManagement import UserList
from telescope.actionHandler import actionHandler
import telescope.utils as utils
from telescope.dbKernel import db

rootdir=os.path.dirname(__file__)


class loggingHandler(tornado.web.RequestHandler):

    def initialize(self):

        self.filename   = 'telescope_server.log'
        self.numEntries = 50

        return


    def get(self):

        logfile    = open(self.filename).read()
        logEntries = logfile.split('\n')

        content = '<div class="page-header">' + \
                '<table class="table table-striped">' + \
                '<thead><tr><th width=100px>logger</th><th>Level</th><th>date</th><th>Message</th></tr></thead>'+ \
                '<tbody>\n'


        for entry in logEntries[-1:-self.numEntries:-1]:

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

        self.render( os.path.join(rootdir,"pages/index.html"),
                    title="Telescope log", content = content,
                    top=open( os.path.join(rootdir,"pages/top.html") ).read(),
                    bottom=open( os.path.join(rootdir,"pages/bottom.html") ).read()
                    )

        return





def monitorLoop( queueMonitor ):
    """
    Loop that keeps updating the monitor in constant
    intervals of time.
    """

    logger = logging.getLogger(__name__)

    while 1:

        logger.info('Queue monitor running...')

        # Updating from server
        queueMonitor.checkQstat()

        # sleeping between each call
        logger.info('Queue monitor sleeping...')

        queueMonitor.sleep()

    return




class server:


    def __init__( self, port = 4000, configFilename='config.ini',
                    telescopeSSHPrivateKey = None, monitoringInterval = 20. ):
        """ This starts the server.
        """

        self.port = str( port )

        ## Setting up the logging
        logging.basicConfig(filename='telescope_server.log',
                            level=logging.DEBUG,
                            format='%(name)s @ %(levelname)s # %(asctime)s -- %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info('Logging setup done.')


        ## Loading configuration file
        config = configparser.ConfigParser()
        config.read( configFilename )
        self.logger.info('Configurations read succesfully.')


        if configFilename == None:

            self.logger.info('Telescope ignoring configuration file.')

            self.credential_username = credentialLoginUsername
            self.credential_password = credentialLoginPassword
            self.remoteServerAddress = credentialServerAddress

            self.logger.info('Credentials set from argument.')

            self.user_names     = listUsernames
            self.user_names_str = utils.stringAllUsersMonitored( self.user_names )

            self.logger.info('Monitored users set from argument.')


            self.database_path = './telescopedb'
            self.logger.info('Database name set from argument.')

        else:
            # Extract name of the account that will be used for log-in
            self.credential_username = config['CREDENTIALS']['USER']
            # Extract the address of the server
            self.remoteServerAddress = config['CREDENTIALS']['SERVER']

            # If there is a password listed, get that
            if config.has_option('CREDENTIALS', 'PASS'):
                self.credential_password = config['CREDENTIALS']['PASS']
            else:
                self.credential_password = ''

            self.logger.info('Credentials parsed from config.ini.')

            # If there is a database listed, get that
            if config.has_option('CONFIGURATION', 'DATABASE'):
                self.database_path = config['CONFIGURATION']['DATABASE']
            else:
                self.database_path = './telescopedb'

            self.logger.info('Database parsed from config.ini.')

            # Create a list of the users whose jobs we'd like to examine
            self.user_names = []
            if config.has_option('MONITOR', 'NUMUSERS') and ( int(config['MONITOR']['NUMUSERS']) > 0 ):
                for ii in range( int(config['MONITOR']['NUMUSERS']) ):
                    self.user_names.append(config['MONITOR']['USER'+str(ii)])

            else:
                self.user_names.append( self.credential_username )

            self.user_names_str = utils.stringAllUsersMonitored( self.user_names )

            self.logger.info('Monitored users parsed from configuration file.')


        self.telescopeSSHPrivateKey = telescopeSSHPrivateKey

        ## Server instance
        self.ServerInterface = SGEServerInterface( self.credential_username,
                                                    self.credential_password,
                                                    self.remoteServerAddress,
                                                    self.user_names )

        ## Databse
        # Access the saved database. If it does not exists,
        # the database is created
        self.logger.info('Setting up the database...')
        self.db = db( self.database_path )
        self.db.createTable()
        self.db.close()
        self.logger.info('Database created.')

        ## Testing SSH connection
        self.logger.info('Testing SSH connection...')
        self.ServerInterface.startSSHconnection()
        self.ServerInterface.closeSSHconnection()
        self.logger.info('Finished testing SSH connection.')

        # Creating a monitor object
        BaseManager.register('jobStatusMonitor', jobStatusMonitor)
        manager = BaseManager()
        manager.start()
        self.queueMonitor = manager.jobStatusMonitor( self.ServerInterface,
                                                        monitoringInterval = monitoringInterval,
                                                        configDatabase = self.database_path )

        ## Starting tornado

        # Defining argument dictionary
        handlerArguments = { 'ServerInterface'     : self.ServerInterface,
                                'queueMonitor'        : self.queueMonitor,
                                'databasePath'        : self.database_path }

        # Setting up handlers
        self.handlers = [
                            (r'/', MainHandler, handlerArguments),
                            (r'/logging', loggingHandler),
                            (r'/experiment', experimentHandler, handlerArguments),
                            (r'/users_list', UserList, handlerArguments),
                            (r'/query', actionHandler, handlerArguments),
                        ]

        ## General settings
        self.settings = dict(
            static_path   = os.path.join( os.path.dirname(__file__), "pages"),
            cookie_secret = base64.b64encode( os.urandom( 80 ) ).decode('ascii')
            )

        self.logger.info('Tornado sectup done.')

        ## Kicking the monitor job
        monitorLoop_process = Process( target=monitorLoop, args=[ self.queueMonitor ])
        monitorLoop_process.start()
        self.logger.info('Parallel status monitor started.')

        ## Starting tornado application
        self.application = web.Application(self.handlers, **self.settings)
        self.logger.info('Tornado web application created.')

        # Set up ctrl C
        signal.signal(signal.SIGINT, self.signal_handler)

        return


    def run(self):
        """
        This method starts tornado ioloop.
        """

        # Setting port to listen
        self.application.listen(self.port)

        print( "Starting data collection (CTRL+C to stop)" )

        self.logger.info('About to start tornado loop...')
        webbrowser.open_new_tab('http://localhost:' + self.port)
        tornado.ioloop.IOLoop.instance().start()

        return


    def signal_handler(self, signal, frame):

        # Printing a message on the screen
        print( "\nStopping..." )

        # Printing log
        self.logger.info('User stopped the server...')
        # Stopping tornado
        tornado.ioloop.IOLoop.instance().stop()
        # Printing log
        self.logger.info('Tornado stopped.')

        # Exiting
        sys.exit(0)

        return


if __name__ == "__main__":
    # This will open a new tab in your default browser
    instance = server()
