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

    def get(self):

        # content = '<p>Test.</p>'
        someRead = self.readFile()
        content = '<p>Test. '+someRead['glossary']['title'] + '</p>'
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
                print "This is the json filename: ",f
                commandString+=dbFileString
                connection.query(commandString)
                cmdOutput = connection.returnedText
                # with open(cmdOutput) as data_file:
                #     data = json.load(data_file)
        connection.close()
        data = json.loads(cmdOutput)

        return data
