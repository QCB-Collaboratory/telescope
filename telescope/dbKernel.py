# sqlite3 database
import sqlite3

# standard libraries
import sys, os, time, io
import datetime



class db:

    def __init__(self, database):

        self.database = database

        self.connection = sqlite3.connect( database = self.database )
        self.connection.isolation_level = None

        return


    def query(self, query):
        cur = self.connection.cursor()
        cur.execute( query )
        return cur

    def close(self):
        self.connection.close()
        return

    def createTable(self):

        #CREATE TABLE Users ( id integer primary key autoincrement, username text, email text, passhash text, salt text ) ;
        #INSERT INTO Users ( username, email, passhash, salt ) VALUES ( '', '', '', '' )

        query = """create table if not exists
                    jobs( jobId INTEGER PRIMARY KEY, jobName TEXT,
                        user VARCHAR(30), status INTEGER,
                        path TEXT, command TEXT, sourceDirectory TEXT, outpath TEXT,
                        memoryRequested TEXT, currentMemory INTEGER, maximumMemory INTEGER,
                        parallel INTEGER, cores INTEGER,
                        clusterNode TEXT,
                        timeAdded VARCHAR(30), runTime TEXT, timeRemaining TEXT,
                        finalRunTime TEXT,finalStatus TEXT
                        );
                """

        self.query( query )

        return


    ##
    ## Inserting and updating user information
    ##

    def getPasswdSalt(self, username):
        query = "SELECT passhash, salt FROM Users WHERE username = '" + username  + "'"
        row = self.query(query).fetchone()
        return row[0], row[1]

    ##
    ## Retrieving information from users
    ##

    def getAllUsers(self):
        query = "SELECT * FROM Users ORDER BY username"
        dataRetrieve = self.query(query).fetchall()
        return self.userParser(dataRetrieve)

    def getPasswdSalt(self, username):
        query = "SELECT passhash, salt FROM Users WHERE username = '" + username  + "'"
        row = self.query(query).fetchone()
        return row[0], row[1]

    ##
    ## Parser for user information
    ##

    def userParser(self, cur ):
        """
        Parser for the tuples from the Users table.
        """
        if(cur):
            curParsed = {}

            for row in cur:
                jobInfo = {}
                jobInfo = self.userTupleParser(row)

                curParsed[ jobInfo["userId"] ] = jobInfo

            return curParsed
        else:
            return None

    def userTupleParser(self, row ):
        """
        Parser for a tuple from the Users table.
        """
        jobInfo = {}
        jobInfo["userId"]   = row[0]
        jobInfo["username"]   = row[1]
        jobInfo["email"]      = row[2]
        jobInfo["passhash"]   = row[3]
        jobInfo["salt"]       = row[4]
        return jobInfo



    ##
    ## Inserting and updating job information
    ##

    def insertJob(self, jobId, jobName, user, status, path, outpath):
        """
        Insert new job.
        """

        if ( not self.checkJob(jobId) ):
            query = "INSERT INTO jobs (jobId, jobName, user, status, path, outpath)"
            query += " VALUES ("+jobId+",'"+jobName+"','"+user+"',"+status
            query += ",'"+path+"','"+outpath+"');"
            self.query( query )
            return True

        else:
            return False


    def checkJob(self, jobId):
        """
        Checks if a job with given jobId is already in the database.
        """
        query = "SELECT jobId FROM jobs WHERE jobId = "+str(jobId)
        curr = self.query( query )

        if( curr.fetchone() ):
            return True
        else:
            return False



    ##
    ## Retrieve information about jobs
    ##

    def getbyjobId(self, jobId):
        """
        Select a single job associated with a given jobId.
        """
        query = "SELECT * FROM jobs WHERE jobId = " + str(jobId)
        row = self.query( query ).fetchone()
        return self.rowParser(row)

    def getAllRunning(self):
        """
        Select all jobs currently marked as running.
        """
        query = "SELECT * FROM jobs WHERE status = 2 ORDER by jobId"
        cur  = self.query( query ).fetchall()
        return  self.curParser(cur)

    def getbyUser_running(self, user):
        """
        Select all jobs currently running associated with the
        same owner user.
        """
        query = "SELECT * FROM jobs WHERE status = 2 and user = '" + str(user) + "' ORDER by jobId"
        cur  = self.query( query ).fetchall()
        return  self.curParser(cur)

    def getAllActive(self):
        """
        Returns all jobs that are registered as either running or
        queued.
        """
        query = "SELECT * FROM jobs WHERE status = 2 OR status = 1 ORDER by jobId"
        cur  = self.query( query ).fetchall()
        return  self.curParser(cur)

    def getAllFinished( self, order = -1 ):
        """
        Retrieve data about finished jobs
        """
        query = "SELECT * FROM jobs WHERE status = 0 ORDER by jobId "
        if order == -1: query += "DESC"
        else:           query += "ASC"

        cur  = self.query( query ).fetchall()

        return  self.curParser(cur)

    def updateStatusbyJobID(self, jobId, newStatus):
        query = "UPDATE jobs SET status = " + str(newStatus) + "  WHERE jobId = " + str(jobId) + ";"
        cur  = self.query( query )
        return


    ##
    ## Job information parser
    ##

    def curParser(self, cur ):
        """
        Parser for the tuples from the jobs table.
        """
        if(cur):
            curParsed = {}

            for row in cur:
                jobInfo = {}
                jobInfo = self.tupleParser(row)

                curParsed[ jobInfo["jobId"] ] = jobInfo

            return curParsed
        else:
            return None



    def rowParser(self, row ):
        """
        Parser for a tuple from the jobs table.
        """

        if(row is not None):

            rowParsed = {}
            jobInfo = {}
            jobInfo = self.tupleParser(row)

            rowParsed[ jobInfo["jobId"] ] = jobInfo

            return rowParsed
        else:
            return None


    def tupleParser(self, row ):
        """
        Parser for a tuple from the jobs table.
        """

        jobInfo = {}
        jobInfo["jobId"]       = row[0]
        jobInfo["jobName"]     = row[1]
        jobInfo["username"]    = row[2]
        jobInfo["jobStatus"]   = row[3]
        jobInfo["workingDir"]  = row[4]
        jobInfo["outputFile"]  = row[7]

        return jobInfo



if __name__ == "__main__":

        db = db( "telescopedb")

        cur = db.getbyUser("jaquejbrito")
        print (cur)
        cur = db.getbyjobId(12)
        print (cur)
