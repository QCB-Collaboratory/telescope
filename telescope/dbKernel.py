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

        query = "SELECT * FROM jobs WHERE status = 2 and jobId = " + str(jobId)

        return self.query( query ).fetchone()


    def getbyUser(self, user):

        query = "SELECT * FROM jobs WHERE status = 2 and user = " + str(user) + " ORDER by jobId"

        return self.query( query ).fetchall()



if __name__ == "__main__":

        db = db( "telescopedb")

        cur = db.getbyUser('user')
        print (cur)
