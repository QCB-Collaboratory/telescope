import logging, time
import os
from builtins import input

# TODO: allow the user to configure which plugin to use
from ansible.plugins.connection import ssh as plugin
from ansible.playbook.play_context import PlayContext


class tlscpSSH:
    """
    Implements a very basic SSH interface to be used by Telescope. It allows
    use of SSH keys and password.
    """

    def __init__(self, username, password='', address = ''):

        logging.info("tlscpSSH: Setting up the client.")

        # Instance of the ssh client
        ctx = PlayContext()
        ctx.remote_user = username
        ctx.password = password
        ctx.remote_addr = address
        self.sshClient = plugin.Connection(ctx, None)

        # TODO: manipulate ConfigManager to set C.HOST_KEY_CHECKING to False

        logging.info("tlscpSSH: Connecting to server <" + address + "> ...")
        logging.info("tlscpSSH: Using username: " + username + " ...")

        self.returnedText = ''

        ### This helps double-checkig the connection was made -- should be re-done!
        # try:
        #     transport = self.sshClient.get_transport()
        #     transport.send_ignore()
        #     self.connectAttemptStatus = 0
        #
        # except EOFError, e:
        #     self.connectAttemptStatus = 0
        ###

        return




    def getQueryResult(self):
        return self.returnedText


    def query(self, command):
        """
        Issues a query to the server. If there is an output,
        the output is then returned as a string in utf-8 encoding.
        """

        # Check if connection is made previously
        if ( self.sshClient ):

            self.returnedText = ''

            returncode, stdout, stderr = self.sshClient.exec_command(command)
            self.returnedText = stdout
            return 1
        else:
            return "No connection."



    def grabStdOut(self, jobName, jobID, workDir, nlines=20):
        filename = jobName + ".o" + jobID
        path2file = os.path.join( workDir, filename )
        return self.grabFile( path2file, nlines=nlines )

    def grabErrOut(self, jobName, jobID, workDir, nlines=20):
        filename = jobName + ".e" + jobID
        path2file = os.path.join( workDir, filename )
        return self.grabFile( path2file, nlines=nlines )

    def grabFile(self, path2file, nlines=20, order = -1 ):
        # TODO: use self.sshClient.fetch_file

        if order == 1:
            readCMD = "head"
        else:
            readCMD = "tail"

        cmd  = readCMD + " -n " + str(nlines) + " " + path2file
        self.query( cmd )
        res = self.returnedText
        self.returnedText = ''
        return res


    def close(self):
        self.sshClient.close()
        return


if __name__ == "__main__":
    userinput = input("What is your username? ")
    connection = tlscpSSH(userinput)
    qstatcommand = "qstat | grep " + userinput
    cmdOutput  = connection.query(qstatcommand)
    print( cmdOutput )
    connection.close()
