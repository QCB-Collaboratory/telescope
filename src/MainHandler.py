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


class MainHandler(tornado.web.RequestHandler):
    """
    Root access
    """

    def get(self):

        self.render('pages/index.html', title="Farore's wind",
                    content = '<p>Test.</p>',
                    top=open(rootdir+"/pages/top.html").read(),
                    bottom=open(rootdir+"/pages/bottom.html").read())

        return
