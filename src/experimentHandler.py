## standard libraries
import sys, os, io
import datetime, time

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



class experimentHandler(tornado.web.RequestHandler):

    def initialize(self, credentialUsername, credentialPass = '',
                    setUsername = [] ):

        self.credentialUsername = credentialUsername
        self.credentialPassword = credentialPass
        self.setUsernames       = setUsername

        return


    def get(self):

        self.jobID        = self.get_argument('jobID', '-1')
        self.outputStatus = self.get_argument('outputFormat', '0')


        if self.jobID == '-1':
            content = "<p>Experiment ID not provided.</p>"

        else:

            ## Connecting to the server through SSH
            connection = tlscpSSH( self.credentialUsername,
                                    password=self.credentialPassword )

            ## Accessing the current status
            connection.query(
                "qstat -u " + self.setUsernames[0] + " | grep " + self.jobID
                )
            curStatus  = connection.returnedText

            ## Accessing the current output
            if self.outputStatus == '1':
                numLines = "200 "  ## cap in 200 lines!
            else:
                numLines = "20 "
            connection.query( "tail -n " + numLines + " telescope_test/output.dat" )
            curOutput  = connection.returnedText

            connection.close()

            ## Constructing the info to post on the web page
            content = self.constructContent(qstat = curStatus, catStat = curOutput)


        ## Rendering the page
        self.render('pages/index.html', title="Farore's wind",
                    content = content,
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return



    def constructContent(self, qstat = '', catStat = ''):
        """
        Constructs the content of the page describing the status of the
        """

        header = "job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID".replace('\t',"&#9;")

        statusLine = qstat.replace('\t',"&#9;")

        content = "<p><b>Status:</b><br />" + header + "<br />" + statusLine + "</p>"
        content += "<p><b>Command:</b> python generate_test.py</p>"

        output2print = catStat.replace('\n', '<br />')

        if self.outputStatus == '1':
            content += "<p><b>Current status of the output:</b></p>"
            content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=0\">here</a> to see the only the last 20 lines of the output file.</p>"


        else:
            content += "<p><b>Latest 20 lines in the output file:</b></p>"
            content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=1\">here</a> to see the full output file.</p>"

        content += "<blockquote>"
        content += output2print
        content += "</blockquote>"


        return content
