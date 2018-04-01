import telescope.utils as utils
from nacl import pwhash, secret, utils as naclutils
import nacl


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
from telescope.server import SGEServerInterface
import telescope.jobStatusMonitor as jobStatusMonitor
from telescope.sshKernel import tlscpSSH
from telescope.dbKernel import db
import telescope.utils as utils

rootdir=os.path.dirname(__file__)


class UserList(tornado.web.RequestHandler):
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

        content = ""

        ## Variables passed through get protocol
        # Getting requested user Id from get, if there is one
        GET_userID  = self.get_argument('userid', '-1')
        # Flag to check if private key should be displayed
        GET_showpvk = self.get_argument('showpvk', '0')

        ## Starting the connection to the databse
        database = db( self.databasePath )

        ## Retrieving information about users

        # If single user was requested, checks if it was found
        uniqueUserFound = False

        # Handling requests for all users
        if GET_userID == '-1':
            listUsers = database.getAllUsers()  ## Getting the list of users
            content += "<h2>List of users</h2>"
        # Handling requests for a single user
        else:
            listUsers = database.getUser_byID(GET_userID)  ## Getting the list of users
            content += "<h2>User details</jh>"
            uniqueUserFound = True


        table_strstart = '''<div class="page-header">
                    <table class="table table-striped">
                    <thead><tr>
                    <th>User name</th>
                    <th>e-mail</th>
                    <th># Active Jobs</th>
                    <th>Another</th>
                    </tr></thead>
                    <tbody>'''

        content += table_strstart

        ## Getting number of users
        numUsers = len( listUsers )

        ## Looping through users
        if numUsers > 0:

            for userId in listUsers.keys():

                # Starting new row
                content += '<tr>'
                # Parsing data from qstat
                userParsed = listUsers[ userId ]

                # Getting the number of active jobs for this user.
                listActiveJobs = database.getbyUser_running( userParsed['userId'] )

                # Evaluating the number of active jobs
                if listActiveJobs == None:
                    numActiveJobs = 'Zero jobs'
                else:
                    numActiveJobs = str(len(listActiveJobs)) + ' jobs'

                # Writing the info into the row
                content +=  '<td><a href="/users_list?userid=' \
                            + str(userParsed['userId']) + '">' \
                            + userParsed['username'][:12]  + '</td>' + \
                            '<td>' + userParsed['email']  + '</td>' + \
                            '<td>' + str(numActiveJobs) + '</td>' + \
                            '<td> </td>'
                ## End of row
                content += '</tr>'

        content += '</tbody></table></div>'


        if uniqueUserFound:

            content += "<h3>SSH private key</h3>"

            if self.ServerInterface.checkEncryptedPrivKey(userParsed['username']):
                content += "<p>User has primary key and it is saved encrypted. "
                content += "<a href=\"/users_list?userid=" \
                            + str(userParsed['userId']) + \
                            "&showpvk=1\">View unencrypted?</a></p>"

                if GET_showpvk == '1':
                    pvkPlainText = self.ServerInterface.decryptPrivKey(userParsed['username'],'')
                    content += "<p style=\"font-size:8pt;\">"
                    content += pvkPlainText.replace('\n', '<br />')
                    content += "</p>"

            else:
                content += "<p>User has no primary key</p>"


        ## Closing the connection with the database
        database.close()

        self.render(os.path.join(rootdir,"pages/index.html"), title="Telescope server",
                    content = content,
                    top=open(os.path.join(rootdir,"pages/top.html")).read(),
                    bottom=open(os.path.join(rootdir,"pages/bottom.html")).read()
                    )

        return
