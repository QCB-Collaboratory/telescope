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


    ## customized queries
    def insertJob(self, jobId, jobName, user, status, path):

        query = "INSERT INTO jobs (jobId, jobName, user, status, path)"
        query += " VALUES ("+jobId+",'"+jobName+"','"+user+"',"+status+",'"+path+"');"
        self.query( query )

        return


if __name__ == "__main__":

        db = db( "telescopedb")

        cur = db.query("select * from jobs")
        db.insertJob('2', 'test', 'username','1', '/home/user')
        v = cur.fetchone()
        print(v[0],",",v[1],",")
