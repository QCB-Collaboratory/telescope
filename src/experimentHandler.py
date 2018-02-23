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





class experimentHandler(tornado.web.RequestHandler):

    def get(self):

        expID        = self.get_argument('expID', '-1')
        outputStatus = self.get_argument('outputFormat', '0')


        if expID == '-1':
            content = "<p>Experiment ID not provided.</p>"

        else:

            ## Grabbing the current state of the output file
            connection = tlscpSSH('thmosque')

            ## Accessing the current status
            connection.query("qstat | grep thmosque")
            curStatus  = connection.returnedText
            time.sleep(0.5)

            ## Accessing the current output
            if outputStatus == '1':
                cmd = "cat "
            else:
                cmd = "tail -n 20 "
            connection.query( cmd + " telescope_test/output.dat" )
            curOutput  = connection.returnedText

            connection.close()

            ## Constructing the info to post on the web page
            header = "job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID".replace('\t',"&#9;")
            content = "<p><b>Status:</b><br />" + header + "<br />" + curStatus.replace('\t',"&#9;") + "</p>"
            content += "<p><b>Command:</b> python generate_test.py</p>"

            output2print = curOutput.replace('\n', '<br />')

            if outputStatus == '1':
                content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=0\">here</a> to see the only the last 20 lines of the output file.</p>"
                content += "<p><b>Current status of the output:</b></p>"

            else:
                content += "<p>Click <a href=\"./experiment?expID=1&outputFormat=1\">here</a> to see the full output file.</p>"
                content += "<p><b>Latest 20 lines:</b></p>"

            content += "<blockquote>"
            content += output2print
            content += "</blockquote>"


        ## Rendering the page
        self.render('pages/index.html', title="Farore's wind",
                    content = content,
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return
