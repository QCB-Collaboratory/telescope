import logging, time
import paramiko
import os


class tlscpSSH:
    """
    Implements a very basic SSH interface to be used by Telescope. It allows
    use of SSH keys and password.
    """

    def __init__(self, username, password='', address = ''):

        logging.info("tlscpSSH: Connecting to server.")

        # Instance of the ssh client
        self.sshClient = paramiko.client.SSHClient()

        # Connect to the server
        self.sshClient.set_missing_host_key_policy( paramiko.client.AutoAddPolicy() )
        self.sshClient.connect(address, username=username,
                                        password=password,
                                        look_for_keys=True
                                )

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

            stdin, stdout, stderr = self.sshClient.exec_command(command)
            while not stdout.channel.exit_status_ready():
                time.sleep(2)
                # Print stdout data
                if stdout.channel.recv_ready():
                    stdin.close()
                    std_out = stdout.readlines()
                    self.returnedText = ''.join(std_out)
                    return 1

                    # the method below, although recommended in the docs,
                    # is returning intermitent Nones...
                    # alldata = stdout.channel.recv(1024)
                    # while stdout.channel.recv_ready():
                    #     alldata += stdout.channel.recv(1024)
                    #
                    # # Print as string with utf8 encoding
                    # string = str(alldata).encode("utf-8")
                    # return string

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
    connection = tlscpSSH('thmosque')
    cmdOutput  = connection.query("qstat | grep thmosque")
    print( cmdOutput )
    connection.close()
