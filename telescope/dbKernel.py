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

        query = "create table if not exists "
        query += "jobs("
        query += "jobId INTEGER PRIMARY KEY,"
        query += "jobName TEXT,"
        query += "user VARCHAR(30), status INTEGER,"
        query += "path TEXT, command TEXT, sourceDirectory TEXT, outpath TEXT,"
        query += "memoryRequested TEXT, currentMemory INTEGER, maximumMemory INTEGER,"
        query += "parallel INTEGER, cores INTEGER,"
        query += "clusterNode TEXT,"
        query += "timeAdded VARCHAR(30), runTime TEXT, timeRemaining TEXT,"
        query += "finalRunTime TEXT,"
        query += "finalStatus TEXT"
        query += ");"

        self.query( query )

        return


    ## customized queries
    def insertJob(self, jobId, jobName, user, status, path, outpath):

        query = "INSERT INTO jobs (jobId, jobName, user, status, path, outpath)"
        query += " VALUES ("+jobId+",'"+jobName+"','"+user+"',"+status
        query += ",'"+path+"','"+outpath+"');"
        self.query( query )

        return

    ## customized queries
    def checkJob(self, jobId):

        query = "SELECT jobId FROM jobs WHERE jobId = "+str(jobId)
        curr = self.query( query )

        if( curr.fetchone() ):
            return True
        else:
            return False

    def getbyjobId(self, jobId):

        query = "SELECT * FROM jobs WHERE jobId = " + str(jobId)

        row = self.query( query ).fetchone()

        return self.rowParser(row)


    def getbyUser(self, user):

        query = "SELECT * FROM jobs WHERE status = 2 and user = '" + str(user) + "' ORDER by jobId"

        cur  = self.query( query ).fetchall()

        return  self.curParser(cur)



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
        jobInfo["jobId"]   = row[0]
        jobInfo["jobName"]   = row[1]
        jobInfo["user"]   = row[2]
        jobInfo["status"]   = row[3]
        jobInfo["path"]   = row[4]
        jobInfo["outpath"]   = row[7]

        return jobInfo



if __name__ == "__main__":

        db = db( "telescopedb")

        cur = db.getbyUser("jaquejbrito")
        print (cur)
        cur = db.getbyjobId(12)
        print (cur)
