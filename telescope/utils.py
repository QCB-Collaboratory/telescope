## XML parser for qstat outputs
import xml.etree.ElementTree as ElementTree


def qstatsXMLParser( status ):
    """
    Parser for the status coming back from qstat.
    """

    qstatParsed = {}

    root = ElementTree.fromstring( status )

    # Usually qstat will have a child for all running jobs,
    # and a child for all queued jobs.

    for childID in range( len(root) ):

        child = root[childID]
        numJobs = len( child )

        for j in range( numJobs ):

            jobInfo = {}

            jobInfo["jobStatus"]   = child[j].attrib["state"]
            jobInfo["jobName"]    = child[j].find('JB_name').text
            jobInfo["jobId"]      = int( child[j].find('JB_job_number').text )

            if child[j].find('JAT_start_time') != None:
                jobInfo["startDate"]     = child[j].find('JAT_start_time').text
            else:
                jobInfo["startDate"]     = ''

            jobInfo["username"] = child[j].find('JB_owner').text

            qstatParsed[ jobInfo["jobId"] ] = jobInfo

    return qstatParsed


def parseStatus2HTML( status ):
    if ( status == 'qw' ) or ( status == 'pending'):
        return '<span style="color: #FF0000;">Queued</span>'

    elif ( status == 'r' ) or ( status == 'running' ):
        return '<span style="color: #00AA00;">Running</span>'

    else:
        return status


status_dict = {
    "running" : 2,
    "pending" : 1
}
def parseStatusCode( status ): return status_dict[status]


def cookieQueryParser( cookieString ):
    splitString = cookieString.split(',')
    if splitString[0].split(':')[1] == "0":
        actionID = 'stop job'
        args = {}
        args['jobid'] = splitString[1].split(':')[1]
    return actionID, args



def stringAllUsersMonitored(listUsers):
    """
    Creates a string with the list of all users to be monitored
    """
    return " " + " ".join( listUsers ) + " "
