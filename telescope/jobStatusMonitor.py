## standard libraries
import sys, os, io
import datetime, time
import numpy as np

## XML parser for qstat outputs
import xml.etree.ElementTree as ElementTree

## Import internal modules
from telescope.sshKernel import tlscpSSH
import telescope.utils as utils
from telescope.dbKernel import db


class jobStatusMonitor:

    def __init__(self, credentialUsername, credentialPassword,
                    remoteServerAddress, setUsernames, setUsernames_str,
                    monitoringInterval = 20., configDatabase="./telescopedb"):

        self.credentialUsername  = credentialUsername
        self.credentialPassword  = credentialPassword
        self.remoteServerAddress = remoteServerAddress
        self.setUsernames        = setUsernames
        self.setUsernames_str    = setUsernames_str

        self.monitoringInterval = monitoringInterval

        self.configDatabase = configDatabase

        self.runningFlag = 1

        # Initializing status variable
        self.curStatusParsed = {}

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
        return self.curStatusParsed


    def checkQstat(self):
        """
        Connects to the server and retrieves the most up to date
        information about the job status.
        """

        # Connecting to the server through SSH
        connection = tlscpSSH( self.credentialUsername,
                                password = self.credentialPassword,
                                address  = self.remoteServerAddress )

        # Accessing the current status
        #connection.query( "qstat -u " + self.setUsernames[0] )
        #self.curStatus = connection.getQueryResult()

        connection.query( "qstat -xml -u " + self.setUsernames_str )
        self.curStatusParsed = utils.qstatsXMLParser( connection.getQueryResult() )

        # Closing the connection to the server
        connection.close()

        # Getting number of jobs
        numJobs = len( self.curStatusParsed )

        if numJobs > 0:

            self.db = db( self.configDatabase )

            # Getting set of keys
            setJobKeys = np.sort( list(self.curStatusParsed.keys()) )

            for jobKey in setJobKeys:

                # Parsing data from qstat
                statParserd = self.curStatusParsed[jobKey]

                # checking if job is not in the database
                if( not self.db.checkJob(statParserd['jid'])):

                    if( str(statParserd['jstate']) == "running" ):
                        status = 2
                    elif( str(statParserd['jstate']) == "queued" ):
                        status = 1
                    else:
                        status = 0

                    self.db.insertJob( str(statParserd['jid']), str(statParserd['jname']), "user", str(status), "path" )

            self.db.close()


        return
