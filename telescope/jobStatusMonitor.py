## standard libraries
import sys, os, io
import datetime, time

## XML parser for qstat outputs
import xml.etree.ElementTree as ElementTree

## Import internal modules
from sshKernel import tlscpSSH
import utils


class jobStatusMonitor:

    def __init__(self, credentialUsername, credentialPassword,
                    setUsernames,
                    monitoringInterval = 20.):

        self.credentialUsername = credentialUsername
        self.credentialPassword = credentialPassword
        self.setUsernames       = setUsernames

        self.monitoringInterval = monitoringInterval


        self.runningFlag = 1

        # Initializing status variable
        self.curStatus = ''

        return


    def getMonitoringInterval(self):
        """
        Returns the interval between each time the status is updated.
        """
        return self.monitoringInterval

    def getMonitorCurrentStatus(self):
        """
        Status text retrieved last time it was updated
        """
        return self.curStatus

    def checkQstat(self):
        """
        Connects to the server and retrieves the most up to date
        information about the job status.
        """

        # Connecting to the server through SSH
        connection = tlscpSSH( self.credentialUsername,
                                password=self.credentialPassword )

        # Accessing the current status
        connection.query( "qstat -u " + self.setUsernames[0] )
        self.curStatus = connection.getQueryResult()

        connection.query( "qstat -xml -u " + self.setUsernames[0] )
        print( self.XMLparser( connection.getQueryResult() ) )

        # Closing the connection to the server
        connection.close()

        return


    def XMLparser(self, XMLinput):
        print( XMLinput )
        root = ElementTree.fromstring( XMLinput )
        for child in root:
            print( child.tag, child.attrib )

        return