import os

from telescope.sshKernel import tlscpSSH
import telescope.utils as utils
from telescope.dbKernel import db

from nacl import pwhash, secret, utils as naclutils
import nacl

class SGEServerInterface:
    """
    Server interface
    """


    def __init__( self, credentialUsername, credentialPassword,
                    remoteServerAddress, setUsernames,
                    databaseName = 'telescopedb'):

        self.credentialUsername     = credentialUsername
        self.credentialPassword     = credentialPassword
        self.remoteServerAddress    = remoteServerAddress

        self.setUsernames           = setUsernames

        self.sshFolder = 'sshKeys/'

        self.databaseName = databaseName

        # Getting string of all monitored users
        self.user_names_str = utils.stringAllUsersMonitored( self.setUsernames )

        return


    ##
    ## SSH connection
    ##

    def startSSHconnection(self, username = ''):
        """
        Connects to the remote server through SSH
        """
        if username == '': username = self.credentialUsername
        self.SSHconnection = tlscpSSH( username,
                                password   = self.credentialPassword,
                                address    = self.remoteServerAddress,
                                privateKey = self.getEncryptedPrivKey(username) )
        return
    
    def closeSSHconnection(self):
        """
        Closes the SSH connection ot the remove server.
        """
        self.SSHconnection.close()
        return


    ##
    ## Handling the private SSH keys
    ##

    def decryptPrivKey( self, username, password ):

        ## Reading the encrypted private key
        privKey_e = self.getEncryptedPrivKey(username)

        ## Retrieving salt
        tlscpDB = db( self.databaseName )
        p_, salt_ = tlscpDB.getPasswdSalt(username)
        tlscpDB.close()

        ## Decrypting the private key
        kdf  = pwhash.argon2i.kdf
        ops  = pwhash.argon2i.OPSLIMIT_SENSITIVE
        mem  = pwhash.argon2i.MEMLIMIT_SENSITIVE
        salt = bytes.fromhex(salt_)                 # salt in 'bytes'
        bpwd = str.encode(password)      # password in 'bytes'
        key  = kdf(secret.SecretBox.KEY_SIZE, bpwd, salt, opslimit=ops, memlimit=mem)
        box  = secret.SecretBox(key)

        received  = box.decrypt( privKey_e, encoder=nacl.encoding.HexEncoder )

        return received.decode('utf-8')


    def getEncryptedPrivKey(self, username ):
        filename = os.path.join( self.sshFolder, 'id_rsa_' + username + '_e' )
        return bytearray( open(filename, 'r').read() , 'utf-8' )



    ##
    ## Querying the server
    ##

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
