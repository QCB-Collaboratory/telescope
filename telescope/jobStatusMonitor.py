## standard libraries
import sys, os, io
import datetime, time
import numpy as np
import logging

## XML parser for qstat outputs
import xml.etree.ElementTree as ElementTree

## Import internal modules
from telescope.sshKernel import tlscpSSH
import telescope.utils as utils
from telescope.dbKernel import db


class jobStatusMonitor:

    def __init__(self, ServerInterface,
                    monitoringInterval = 20., monitoringSubInterval = 1.,
                    configDatabase="./telescopedb"):

        ## ServerInterface object
        self.ServerInterface = ServerInterface

        self.monitoringInterval     = monitoringInterval
        self.monitoringSubInterval  = monitoringSubInterval
        self.numSleepIntervals      = int( monitoringInterval / monitoringSubInterval ) + 1
        self.currentSleepStep       = 0

        self.configDatabase = configDatabase

        self.runningFlag = 1
        self.updateNow   = False

        # Initializing status variable
        self.curStatusParsed = {}

        return


    def sleep(self):

        # Initializing the count of time intervals
        self.currentSleepStep = 0

        while self.currentSleepStep <= self.numSleepIntervals:

            # sleep for one more time interval
            time.sleep( self.monitoringSubInterval )
            self.currentSleepStep += 1

            # check if update request was issued
            if self.updateNow:
                self.currentSleepStep = 0
                self.updateNow = False
                return

        return

    def requestUpdate(self):
        self.updateNow = True
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

        logging.info("statusMonitor: Getting started.")

        ## Connecting to the server
        logging.info("statusMonitor: openning SSH connection.")
        self.ServerInterface.startSSHconnection()

        ## Grabbing the result of qstat
        logging.info("statusMonitor: Retrieving and parsing qstat.")
        self.curStatusParsed = utils.qstatsXMLParser( self.ServerInterface.qstatQuery() )

        ## Connecting to the databse
        logging.info("statusMonitor: Connecting to the database.")
        self.db = db( self.configDatabase )

        # Getting number of jobs
        numJobs = len( self.curStatusParsed )


        logging.info("statusMonitor: Looping through the jobs")
        if numJobs > 0:

            # Getting set of keys
            setJobKeys = np.sort( list(self.curStatusParsed.keys()) )

            for jobKey in setJobKeys:

                # Parsing data from qstat
                statParserd = self.curStatusParsed[jobKey]

                # checking if job is not in the database yet
                if( not self.db.checkJob( statParserd['jobId'] ) ):

                    if( str(statParserd['jobStatus']) == "running" ):
                        status = 2
                    elif( str(statParserd['jobStatus']) == "pending" ):
                        status = 1
                    else:
                        status = 0

                    ## Retrieving details about the job
                    curStatJ = self.ServerInterface.qstatJobQuery(statParserd['jobId'] )
                    sgeScriptRun = curStatJ.split( 'script_file:' )[1].split('\n')[0].replace(' ','')
                    sgeOWorkDir  = curStatJ.split( 'sge_o_workdir:' )[1].split('\n')[0].replace(' ','')

                    ## Figuring out the output path
                    # Standard SGE output
                    outpath = statParserd['jobName'] + ".o" + str(statParserd['jobId'])

                    # Checking for custom output path
                    curStatJ = self.ServerInterface.queryGrep( os.path.join(sgeOWorkDir,sgeScriptRun), "TELESCOPE-WATCH-OUTPUT")
                    if "TELESCOPE-WATCH-OUTPUT:" in curStatJ:
                        outpath = curStatJ.split("TELESCOPE-WATCH-OUTPUT:")[1].strip(' \t\n\r')

                    ## Inserting data about the job into the database
                    self.db.insertJob( str(statParserd['jobId']),
                                        str(statParserd['jobName']),
                                        str(statParserd['username']),
                                        str(status),
                                        sgeOWorkDir,
                                        outpath )


        db_allActive = self.db.getAllActive()
        if self.curStatusParsed != None and db_allActive != None:
            list_keys_inDB = db_allActive.keys()

            for key in list_keys_inDB:
                # Updating the status of finished jobs
                if not( key  in self.curStatusParsed.keys() ):
                    self.db.updateStatusbyJobID(key, 0)

                # Updating the status of running jobs
                else:
                    curStatusCode = utils.parseStatusCode( self.curStatusParsed[key]["jobStatus"] )
                    if db_allActive[key]["jobStatus"] != curStatusCode:
                        self.db.updateStatusbyJobID(key, curStatusCode)

        # Closing the connection to the database
        self.db.close()

        # Closing the connection to the server
        self.ServerInterface.closeSSHconnection()


        logging.info("statusMonitor: finished.")

        return
