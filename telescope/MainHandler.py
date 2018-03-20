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
import telescope.utils as utils

rootdir=os.path.dirname(__file__)


class MainHandler(tornado.web.RequestHandler):
    """
    Root access
    """

    def initialize(self, credentialUsername, credentialPass, remoteServerAddress,
                    setUsername, queueMonitor ):

        # Credentials for log in
        self.credentialUsername  = credentialUsername
        self.credentialPassword  = credentialPass
        self.remoteServerAddress = remoteServerAddress

        # Usernames to keep track of
        self.setUsernames = setUsername

        # Server's queue monitoringInterval
        self.queueMonitor = queueMonitor

        return



    def get(self):

        content = "<p>Welcome to Telescope Server! Below you will find a list of your jobs. Click on the job ID to see more details.</p>"

        content += '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
                    '<thead><tr>' + \
                    '<th width=100px>Job ID</th>' + \
                    '<th>Job name</th>' + \
                    '<th>state</th>' + \
                    '<th>Started in</th>' + \
                    '</tr></thead>'+ \
                    '<tbody>\n'

        # Grabt the latest status from the servers
        curStatus  = self.queueMonitor.getMonitorCurrentStatus()
        # Getting number of jobs
        numJobs = len( curStatus )


        if numJobs > 0:

            # Getting set of keys
            setJobKeys = np.sort( list(curStatus.keys()) )

            for jobKey in setJobKeys:

                # Starting new row
                content += '<tr>'
                # Parsing data from qstat
                statParserd = curStatus[jobKey]

                # Writing the info into the row
                content +=  '<td><a href="/experiment?jobID=' + str(statParserd['jid']) + '">' + \
                            str(statParserd['jid']) + '</a></td>' + \
                            '<td>' + statParserd['jname']  + '</td>' + \
                            '<td>' + \
                            utils.parseStatus2HTML( statParserd['jstate'] ) \
                            + '</td>' + \
                            '<td>' + statParserd['date']   + '</td>'
                ## End of row
                content += '</tr>'

        content += '</tbody></table></div>'


        self.render(os.path.join(rootdir,"pages/index.html"), title="Telescope server",
                    content = content,
                    top=open(os.path.join(rootdir,"pages/top.html")).read(),
                    bottom=open(os.path.join(rootdir,"pages/bottom.html")).read()
                    )

        return




    def readFile(self,dbFileString = ".telescope.json"):
        """
        Find some file that gives you the information to display in a list of
        hyperlinks
        """
        commandString = "cat "
        connection = tlscpSSH( self.credentialUsername,
                                password=self.credentialPassword,
                                address=self.remoteServerAddress )
        cmdOutput = ""
        listquery = "ls -a"
        connection.query(listquery)
        cmdOutput = connection.returnedText
        cmdOutput = cmdOutput.split('\n')
        for f in cmdOutput:
            if f == dbFileString: # Change this to something less hard coded?
                print( "This is the json filename: ", f )
                commandString+=dbFileString
                connection.query(commandString)
                cmdOutput = connection.returnedText
                # with open(cmdOutput) as data_file:
                #     data = json.load(data_file)
        connection.close()
        data = json.loads(cmdOutput)

        return data
