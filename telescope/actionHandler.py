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
from telescope.sshKernel import tlscpSSH
from telescope.dbKernel import db
import telescope.utils as utils

rootdir=os.path.dirname(__file__)


class actionHandler(tornado.web.RequestHandler):
    """
    Root access
    """

    def initialize(self, credentialUsername, credentialPass,
                    remoteServerAddress, tlscpSSHPrivateKey,
                    setUsername, setUsername_str, queueMonitor, databasePath ):

        # Credentials for log in
        self.credentialUsername  = credentialUsername
        self.credentialPassword  = credentialPass
        self.remoteServerAddress = remoteServerAddress
        self.tlscpSSHPrivateKey  = tlscpSSHPrivateKey

        # Usernames to keep track of
        self.setUsernames     = setUsername
        self.setUsernames_str = setUsername_str

        # Server's queue monitoringInterval
        self.queueMonitor = queueMonitor

        self.databasePath = databasePath

        return



    def get(self):

        self.jobID     = self.get_argument('jobID', '-1')
        self.action    = self.get_argument('act', '-1')

        if self.jobID != '-1':

            ## Connecting to the server through SSH
            connection = tlscpSSH( self.credentialUsername,
                                    password   = self.credentialPassword,
                                    address    = self.remoteServerAddress,
                                    privateKey = self.tlscpSSHPrivateKey )


            if self.action == '0':
                # Querying the system
                connection.stopJob( self.jobID )
                # Requesting an update from the queue monitor
                self.queueMonitor.requestUpdate()
                # Giving it some time to take effect
                time.sleep(1.2)

            ## Closing the SSH connection
            connection.close()

        content = "<script>window.location.replace('/');</script>"
        self.render(os.path.join(rootdir,"pages/index.html"), title="Telescope server",
                    content = content,
                    top=open(os.path.join(rootdir,"pages/top.html")).read(),
                    bottom=open(os.path.join(rootdir,"pages/bottom.html")).read()
                    )

        return
