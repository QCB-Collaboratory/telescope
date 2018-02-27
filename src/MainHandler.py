## standard libraries
import sys, os, io
import datetime, time
import json

## to create threads
import multiprocessing as mp

## For the web service
import tornado.ioloop
import tornado.web as web
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient
import logging


## Import internal modules
from sshKernel import tlscpSSH


rootdir='./'


class MainHandler(tornado.web.RequestHandler):
    """
    Root access
    """
    def initialize(self, credentialUsername, credentialPass = '',
                    setUsername = [] ):

        self.credentialUsername = credentialUsername
        self.credentialPassword = credentialPass
        self.setUsernames       = setUsername

        return


    def qstatsParser(self, statusLine):
        """
        Parser for the status coming back from qstat.
        """

        ## Splitting by space
        statusLine_split = statusLine.split(' ')

        ## Dictionary to store the info
        parsed = {}

        ## Parsing job id, name and timestamp when job started
        parsed['jid']    = statusLine_split[0]
        parsed['jname']  = statusLine_split[2]
        parsed['date']   = statusLine_split[13] + ' ' + statusLine_split[14]

        ## Parsing the status column

        if statusLine_split[8] == 'qw':
            parsed['jstate'] = '<span style="color: #FF0000;">Queued</span>'

        if statusLine_split[8] == 'r':
            parsed['jstate'] = '<span style="color: #00AA00;">Running</span>'

        else:
            parsed['jstate'] = statusLine_split[8]

        return parsed



    def get(self):

        ## Connecting to the server through SSH
        connection = tlscpSSH( self.credentialUsername,
                                password=self.credentialPassword )

        ## Accessing the current status
        connection.query( "qstat -u " + self.setUsernames[0] )
        curStatus  = connection.returnedText



        content = "<p>Welcome to Telescope Server! Below you will find a list of your jobs. Click on the job ID to see more details.</p>"

        # Splitting string per line
        curStatus_splist = curStatus.split('\n')

        content += '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
                    '<thead><tr>' + \
                    '<th width=100px>Job ID</th>' + \
                    '<th>Job name</th>' + \
                    '<th>state</th>' + \
                    '<th>Started</th>' + \
                    '</tr></thead>'+ \
                    '<tbody>\n'

        for j in range(2, len(curStatus_splist) - 3 ):
            # Starting new row
            content += '<tr>'
            # Parsing data from qstat
            statParserd = self.qstatsParser( curStatus_splist[j] )
            # Writing the info into the row
            content +=  '<td><a href="/experiment?jobID=' + statParserd['jid'] + '">' + \
                        statParserd['jid']    + '</a></td>' + \
                        '<td>' + statParserd['jname']  + '</td>' + \
                        '<td>' + statParserd['jstate'] + '</td>' + \
                        '<td>' + statParserd['date']   + '</td>'
            ## End of row
            content += '</tr>'

        content += '</tbody></table></div>'


        self.render('pages/index.html', title="Farore's wind",
                    content = content,
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return

    def readFile(self,dbFileString = ".telescope.json"):
        """
        Find some file that gives you the information to display in a list of
        hyperlinks
        """
        commandString = "cat "
        connection = tlscpSSH( self.credentialUsername,
                                password=self.credentialPassword )
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
