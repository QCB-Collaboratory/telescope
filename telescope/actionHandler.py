## standard libraries
import sys, os, io
import datetime, time
import json
import numpy as np

## For the web service
import tornado.ioloop
import tornado.web as web
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient
import logging


## Import internal modules
import telescope.jobStatusMonitor as jobStatusMonitor
from telescope.server import SGEServerInterface
from telescope.sshKernel import tlscpSSH
from telescope.dbKernel import db
import telescope.utils as utils

rootdir=os.path.dirname(__file__)


class actionHandler(tornado.web.RequestHandler):
    """
    Root access
    """

    def initialize(self, ServerInterface, queueMonitor, databasePath ):

        ## ServerInterface object
        self.ServerInterface = ServerInterface

        # Server's queue monitoringInterval
        self.queueMonitor = queueMonitor

        self.databasePath = databasePath

        return



    def get(self):

        self.jobID     = self.get_argument('jobID', '-1')
        self.action    = self.get_argument('act', '-1')

        if self.jobID != '-1':

            ## Connecting to the server through SSH
            self.ServerInterface.startSSHconnection()

            if self.action == '0':

                self.set_secure_cookie( "query", "a:" + str(self.action) + ",jid:" + str(self.jobID)  )

                # Querying the system
                self.ServerInterface.killJob( self.jobID )
                # Requesting an update from the queue monitor
                self.queueMonitor.requestUpdate()
                # Giving it some time to take effect
                time.sleep(1.5)

            ## Closing the SSH connection
            self.ServerInterface.closeSSHconnection()

        content = "<script>window.location.replace('/');</script>"
        self.render(os.path.join(rootdir,"pages/index.html"), title="Telescope server",
                    content = content,
                    top=open(os.path.join(rootdir,"pages/top.html")).read(),
                    bottom=open(os.path.join(rootdir,"pages/bottom.html")).read()
                    )

        return
