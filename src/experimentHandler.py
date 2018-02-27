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
import utils


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

            statParserd = utils.qstatsParser( curStatus.split('\n')[0] )

            connection.query( "qstat -j " + self.jobID )
            curStatJ    = connection.returnedText
            sgeOWorkDir = curStatJ.split( 'sge_o_workdir:' )[1].split('\n')[0].replace(' ','')

            ## Accessing the current output
            if self.outputStatus == '1':
                numLines = 200  ## cap in 200 lines!
            else:
                numLines = 20

            curOutput  = connection.grabStdOut( statParserd['jname'],
                                                self.jobID,
                                                sgeOWorkDir, nlines=numLines )

            curErrMsg  = connection.grabErrOut( statParserd['jname'],
                                                self.jobID,
                                                sgeOWorkDir, nlines=numLines )

            connection.close()
            
            ## Constructing the info to post on the web page
            content = self.constructContent( qstat = curStatus,
                                             catStat = curOutput,
                                             catErrm = curErrMsg
                                            )


        ## Rendering the page
        self.render('pages/index.html', title="Farore's wind",
                    content = content,
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return




    def constructContent(self, qstat = '', catStat = '', catErrm = ''):
        """
        Constructs the content of the page describing the status of the
        """

        header = "job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID".replace('\t',"&#9;")

        statusLine = qstat.replace('\t',"&#9;")

        content = "<p><b>Status:</b><br />" + header + "<br />" + statusLine + "</p>"
        content += "<p><b>Command:</b> python generate_test.py</p>"

        output2print = catStat.replace('\n', '<br />')

        if self.outputStatus == '1':
            content += "<h2>Current status of the output</h2>"
            content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=0\">here</a> to see the only the last 20 lines of the output file.</p>"
        else:
            content += "<h2>Current status of the output (last 20 lines)</h2>"
            content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=1\">here</a> to see the full output file.</p>"

        content += "<blockquote>"
        content += output2print
        content += "</blockquote>"


        output2print = catErrm.replace('\n', '<br />')

        if self.outputStatus == '1':
            content += "<h2>Error messages:</h2>"
            content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=0\">here</a> to see the only the last 20 lines of the output file.</p>"
        else:
            content += "<h2>Error messages (last 20 lines):</h2>"
            content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=1\">here</a> to see the full output file.</p>"

        content += "<blockquote>"
        content += output2print
        content += "</blockquote>"

        return content
