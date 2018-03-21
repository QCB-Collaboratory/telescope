## XML parser for qstat outputs
import xml.etree.ElementTree as ElementTree


def qstatsXMLParser( status ):
    """
    Parser for the status coming back from qstat.
    """

    qstatParsed = {}

    root = ElementTree.fromstring( status )
    numJobs = len( root[0] )

    for j in range( numJobs ):
        jobInfo = {}
        jobInfo["jstate"]   = root[0][j].attrib["state"]
        jobInfo["jname"]    = root[0][j].find('JB_name').text
        jobInfo["jid"]      = int( root[0][j].find('JB_job_number').text )
        jobInfo["date"]     = root[0][j].find('JAT_start_time').text
        jobInfo["username"] = root[0][j].find('JB_owner').text

        qstatParsed[ jobInfo["jid"] ] = jobInfo

    return qstatParsed


def parseStatus2HTML( status ):
    if ( status == 'qw' ) or ( status == 'queued'):
        return '<span style="color: #FF0000;">Queued</span>'

    elif ( status == 'r' ) or ( status == 'running' ):
        return '<span style="color: #00AA00;">Running</span>'

    else:
        return status



def stringAllUsersMonitored(listUsers):
    """
    Creates a string with the list of all users to be monitored
    """
    return " " + " ".join( listUsers ) + " "
