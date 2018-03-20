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
        jobInfo["jstate"] = root[0][j].attrib["state"]
        jobInfo["jname"]  = root[0][j].find('JB_name').text
        jobInfo["jid"]    = int( root[0][j].find('JB_job_number').text )
        jobInfo["date"]   = root[0][j].find('JAT_start_time').text

        qstatParsed[ jobInfo["jid"] ] = jobInfo

    return qstatParsed


def parseStatus2HTML( status ):
    if ( status == 'qw' ) or ( status == 'queued'):
        return '<span style="color: #FF0000;">Queued</span>'

    elif ( status == 'r' ) or ( status == 'running' ):
        return '<span style="color: #00AA00;">Running</span>'

    else:
        return status




def qstatsParser(statusLine):
    """
    Parser for the status coming back from qstat.
    """

    ## Splitting by space
    statusLine_split = statusLine.split(' ')

    ## Dictionary to store the info
    parsed = {}

    ## Parsing job id, name and timestamp when job started
    parsed['jid']    = statusLine_split[0]
    parsed['jname']  = statusLine_split[2]
    parsed['date']   = statusLine_split[17] + ' ' + statusLine_split[18]

    ## Parsing the status column

    if statusLine_split[12] == 'qw':
        parsed['jstate'] = '<span style="color: #FF0000;">Queued</span>'

    elif statusLine_split[12] == 'r':
        parsed['jstate'] = '<span style="color: #00AA00;">Running</span>'

    else:
        parsed['jstate'] = statusLine_split[8]

    return parsed
