import logging, time
import paramiko


class tlscpSSH:
    """
    Implements a very basic SSH interface to be used by Telescope. It allows
    use of SSH keys and password.
    """

    def __init__(self, username, password='', address = 'hoffman2.idre.ucla.edu'):

        logging.info("tlscpSSH: Connecting to server.")

        # Instance of the ssh client
        self.sshClient = paramiko.client.SSHClient()

        # Connect to the server
        self.sshClient.set_missing_host_key_policy( paramiko.client.AutoAddPolicy() )
        self.sshClient.connect(address, username=username,
                                        password=password,
                                        look_for_keys=True
                                )

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



    def query(self, command):
        """
        Issues a query to the server. If there is an output,
        the output is then returned as a string in utf-8 encoding.
        """

        # Check if connection is made previously
        if ( self.sshClient ):

            stdin, stdout, stderr = self.sshClient.exec_command(command)
            while not stdout.channel.exit_status_ready():
                time.sleep(2)
                # Print stdout data
                if stdout.channel.recv_ready():
                    stdin.close()
                    std_out = stdout.readlines()
                    print( ''.join(std_out) )
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



    def close(self):
        self.sshClient.close()
        return


if __name__ == "__main__":
    connection = tlscpSSH('thmosque')
    cmdOutput  = connection.query("qstat | grep thmosque")
    print( cmdOutput )
    connection.close()
