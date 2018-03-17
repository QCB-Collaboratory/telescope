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
    print(statusLine_split)
    if statusLine_split[12] == 'qw':
        parsed['jstate'] = '<span style="color: #FF0000;">Queued</span>'

    elif statusLine_split[12] == 'r':
        parsed['jstate'] = '<span style="color: #00AA00;">Running</span>'

    else:
        parsed['jstate'] = statusLine_split[8]

    return parsed
