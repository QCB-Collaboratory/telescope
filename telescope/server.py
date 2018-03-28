import os

from telescope.sshKernel import tlscpSSH
import telescope.utils as utils


class SGEServerInterface:
    """
    Server interface
    """


    def __init__( self, credentialUsername, credentialPassword,
                    remoteServerAddress,
                    setUsernames):

        self.credentialUsername     = credentialUsername
        self.credentialPassword     = credentialPassword
        self.remoteServerAddress    = remoteServerAddress

        self.setUsernames           = setUsernames

        self.sshFolder = 'sshKeys/'

        # Getting string of all monitored users
        self.user_names_str = utils.stringAllUsersMonitored( self.setUsernames )

        return


    def privKey(self, username ):
        return os.path.join( self.sshFolder, 'id_rsa_' + username)


    def startSSHconnection(self, username = ''):
        """
        Connects to the remote server through SSH
        """
        if username == '': username = self.credentialUsername
        self.SSHconnection = tlscpSSH( username,
                                password   = self.credentialPassword,
                                address    = self.remoteServerAddress,
                                privateKey = self.privKey(username) )
        return


    def closeSSHconnection(self):
        """
        Closes the SSH connection ot the remove server.
        """
        self.SSHconnection.close()
        return


    def qstatQuery(self, usernames = '', xml=True):
        """
        Executes on the remote server the following command: qstat -u <usernames>
        """
        if xml: xmlstr = " -xml "
        else:   xmlstr = ""
        if usernames == '': usernames = self.user_names_str
        self.SSHconnection.query( "qstat " + xmlstr + " -u " + usernames )
        return self.SSHconnection.getQueryResult()


    def qstatJobQuery(self, jobID, xml=False):
        """
        Executes on the remote server the following command: qstat -j <jobID>
        """
        if xml: xmlstr = " -xml "
        else:   xmlstr = ""
        self.SSHconnection.query( "qstat  " + xmlstr + " -j " + str(jobID) )
        return self.SSHconnection.getQueryResult()


    def killJob(self, jobID):
        """
        Kills the job identified by <jobID> on the remote server
        """
        self.SSHconnection.query( "qdel " + str(jobID) )
        return

    def grabFile(self, path2file, nlines=20, order = -1 ):
        """
        Returns the content of a file
        """

        if order == 1:
            readCMD = "head"
        else:
            readCMD = "tail"

        cmd  = readCMD + " -n " + str(nlines) + " " + path2file
        self.SSHconnection.query( cmd )
        res = self.SSHconnection.returnedText
        self.SSHconnection.returnedText = ''

        return res

    def grabStdOut(self, jobName, jobID, workDir, nlines=20):
        filename = jobName + ".o" + jobID
        path2file = os.path.join( workDir, filename )
        return self.grabFile( path2file, nlines=nlines )

    def grabErrOut(self, jobName, jobID, workDir, nlines=20):
        filename = jobName + ".e" + jobID
        path2file = os.path.join( workDir, filename )
        return self.grabFile( path2file, nlines=nlines )


## the end my friend
