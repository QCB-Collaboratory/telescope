import logging, time
import paramiko
import os
from builtins import input


class tlscpSSH:
    """
    Implements a very basic SSH interface to be used by Telescope. It allows
    use of SSH keys and password.
    """

    def __init__(self, username, password='', address = '',
                    privateKey = None ):

        logging.info("tlscpSSH: Setting up the client.")

        if privateKey != None:
            privkey = paramiko.RSAKey.from_private_key_file( privateKey )

        # Instance of the ssh client
        self.sshClient = paramiko.client.SSHClient()

        # Connect to the server
        self.sshClient.set_missing_host_key_policy( paramiko.client.AutoAddPolicy() )

        logging.info("tlscpSSH: Connecting to server <" + address + "> ...")
        logging.info("tlscpSSH: Using username: " + username + " ...")

        if privateKey == None :
            self.sshClient.connect(address, username=username,
                                            password=password,
                                            look_for_keys=True
                                            )
        else:
            self.sshClient.connect(address, username=username,
                                            password=password,
                                            pkey = privkey,
                                            look_for_keys=True
                                            )

        logging.info("tlscpSSH: Connected.")

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
                time.sleep(0.1)
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



    def stopJob( self, jobID ):
        logging.info("tlscpSSH: stopJob method called on jobID = " + str(jobID) )
        cmd  = "qdel " + str(jobID)
        self.query( cmd )
        logging.info("tlscpSSH: Command issued. Returning...")
        res = self.returnedText
        self.returnedText = ''
        return res


    def grabFile(self, path2file, nlines=20, order = -1 ):
        """
        depracated!!!
        """

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
