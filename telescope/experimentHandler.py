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
from telescope.sshKernel import tlscpSSH
import telescope.utils as utils

rootdir=os.path.dirname(__file__)

class experimentHandler(tornado.web.RequestHandler):

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

        self.jobID        = self.get_argument('jobID', '-1')
        self.outputStatus = self.get_argument('outputFormat', '0')


        if self.jobID == '-1':
            content = "<p>Experiment ID not provided.</p>"

        else:

            # Grabt the latest status from the servers
            curStatus  = self.queueMonitor.getMonitorCurrentStatus().split('\n')
            curStatus = [ s for s in curStatus if self.jobID in s ][0]
            statParserd = utils.qstatsParser( curStatus )

            ## Connecting to the server through SSH
            connection = tlscpSSH( self.credentialUsername,
                                    password=self.credentialPassword,
                                    address=self.remoteServerAddress )
            connection.query( "qstat -j " + self.jobID )
            curStatJ     = connection.returnedText
            # Name of the script
            sgeScriptRun = curStatJ.split( 'script_file:' )[1].split('\n')[0].replace(' ','')
            # Working directory
            sgeOWorkDir  = curStatJ.split( 'sge_o_workdir:' )[1].split('\n')[0].replace(' ','')
            # Capturing Job Name -- if job name is too long, qstat only shows
            # the beginning of the job name. This ensures we get the full name.
            sgeJobName   = curStatJ.split( 'job_name:' )[1].split('\n')[0].replace(' ','')

            ## Accessing the current output
            if self.outputStatus == '1':
                numLines = 200  ## cap in 200 lines!
            else:
                numLines = 20

            curOutput  = connection.grabStdOut( sgeJobName, self.jobID,
                                                sgeOWorkDir, nlines=numLines )

            curErrMsg  = connection.grabErrOut( sgeJobName, self.jobID,
                                                sgeOWorkDir, nlines=numLines )

            scriptContent = connection.grabFile(sgeOWorkDir + '/' + sgeScriptRun,
                                                nlines=20, order=1 )

            connection.close()

            ## Constructing the info to post on the web page
            content = self.constructContent( qstat = curStatus, qstat_parsed=statParserd,
                                             catStat = curOutput,
                                             catErrm = curErrMsg,
                                             workDir = sgeOWorkDir,
                                             scriptName = sgeScriptRun,
                                             scriptContent = scriptContent
                                            )


        ## Rendering the page
        self.render('pages/index.html', title="Farore's wind",
                    content = content,
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return




    def constructContent(self, qstat = '', qstat_parsed = [], catStat = '', catErrm = '',
                            workDir = '', scriptName = '', scriptContent = ''):
        """
        Constructs the content of the page describing the status of the
        """

        content = '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
                    '<thead><tr>' + \
                    '<th width=100px>Job ID</th>' + \
                    '<th>Job name</th>' + \
                    '<th>State</th>' + \
                    '<th>Started in</th>' + \
                    '</tr></thead>'+ \
                    '<tbody>\n'


        # Starting new row
        content += '<tr>'
        # Writing the info into the row
        content +=  '<td><a href="/experiment?jobID=' + qstat_parsed['jid'] + '">' + \
                    qstat_parsed['jid']    + '</a></td>' + \
                    '<td>' + qstat_parsed['jname']  + '</td>' + \
                    '<td>' + qstat_parsed['jstate'] + '</td>' + \
                    '<td>' + qstat_parsed['date']   + '</td>'
        ## End of row
        content += '</tr>'
        content += '</tbody></table></div>'

        content += "<p><b>Script name:</b> " + scriptName + "</p>"
        content += "<p><b>Directory:</b> " + workDir + "</p>"

        content += "<h3>Content of the script file:</h3>"
        content += "<blockquote>" + scriptContent.replace('\n', '<br />') + "</blockquote>"


        if self.outputStatus == '1':
            content += "<h3>Current status of the output</h3>"
            #content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=0\">here</a> to see the only the last 20 lines of the output file.</p>"
        else:
            content += "<h3>Current status of the output (last 20 lines)</h3>"
            #content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=1\">here</a> to see the full output file.</p>"

        content += "<blockquote>" + catStat.replace('\n', '<br />') + "</blockquote>"


        if self.outputStatus == '1':
            content += "<h3>Error messages:</h3>"
            #content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=0\">here</a> to see the only the last 20 lines of the output file.</p>"
        else:
            content += "<h3>Error messages (last 20 lines):</h3>"
            #content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=1\">here</a> to see the full output file.</p>"

        content += "<blockquote>" + catErrm.replace('\n', '<br />') + "</blockquote>"

        return content
