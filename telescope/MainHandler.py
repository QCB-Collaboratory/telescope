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


class MainHandler(tornado.web.RequestHandler):
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

        content = "<p>Welcome to Telescope Server! Below you will find a list of your jobs. Click on the job ID to see more details.</p>"


        table_strstart = '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
                    '<thead><tr>' + \
                    '<th width=100px>Job ID</th>' + \
                    '<th width=100px>User</th>' + \
                    '<th>Job name</th>' + \
                    '<th>state</th>' + \
                    '<th>Started in</th>' + \
                    '</tr></thead>'+ \
                    '<tbody>\n'

        content += table_strstart

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
                            '<td>' + statParserd['username'][:8]  + '</td>' + \
                            '<td>' + statParserd['jname']  + '</td>' + \
                            '<td>' + \
                            utils.parseStatus2HTML( statParserd['jstate'] ) \
                            + '</td>' + \
                            '<td>' + statParserd['date']   + '</td>'
                ## End of row
                content += '</tr>'

        content += '</tbody></table></div>'

        self.db = db( self.databasePath )
        parsedFinishedJobs = self.db.getAllFinished()
        self.db.close()

        if parsedFinishedJobs != None:
            if len( parsedFinishedJobs ) > 0:

                content += "<br /><h3>List of finished jobs (under development)</3>" + table_strstart

                # Getting set of keys
                setJobKeys = np.sort( list(parsedFinishedJobs.keys()) )

                for jobKey in setJobKeys:

                    # Starting new row
                    content += '<tr>'
                    # Parsing data from qstat
                    statParserd = parsedFinishedJobs[jobKey]

                    # Writing the info into the row
                    content +=  '<td>' + \
                                str(statParserd['jobId']) + '</a></td>' + \
                                '<td>' + statParserd['user'][:8]  + '</td>' + \
                                '<td>' + statParserd['jobName']  + '</td>' + \
                                '<td>Finished with status 0</td>' + \
                                '<td>--</td>'
                    ## End of row
                    content += '</tr>'

                content += '</tbody></table></div>'


        if curStatus == {}:
            content += "<script>setTimeout(function(){ window.location.reload(1); }, 1000);</script>"

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
