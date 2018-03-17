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
    parsed['date']   = statusLine_split[13] + ' ' + statusLine_split[14]

    ## Parsing the status column

    if statusLine_split[8] == 'qw':
        parsed['jstate'] = '<span style="color: #FF0000;">Queued</span>'

    elif statusLine_split[8] == 'r':
        parsed['jstate'] = '<span style="color: #00AA00;">Running</span>'

    else:
        parsed['jstate'] = statusLine_split[8]

    return parsed
