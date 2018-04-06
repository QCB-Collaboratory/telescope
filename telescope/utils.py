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


def qstatsJXMLParser(status):
    """
    Parser for the status coming back from qstat -j.
    """

    # root = status.getroot()
    root = ElementTree.fromstring(status)
    child = root[0] # Get djob_info
        
    qstatParsed = {}

    numJobs = len(child)
    for i in range(numJobs):

        jobInfo = {} # Empty dict to be filled with qstat -j -xml

        jobInfo["username"]  = child[i].find('JB_owner').text
        jobInfo["group"]     = child[i].find('JB_group').text
        jobInfo["project"]   = child[i].find('JB_project').text
        jobInfo["jobName"]   = child[i].find('JB_job_name').text
        jobInfo["jobId"]     = int(child[i].find('JB_job_number').text)
        
        resourceRequests = child[i].find('JB_hard_resource_list').findall('qstat_l_requests')
        numResources = len(resourceRequests)

        for j in range(numResources):

            currentResName = resourceRequests[j].find('CE_name').text
            currentResValue = resourceRequests[j].find('CE_stringval').text

            if currentResName == 'highp':
                jobInfo["highp"] = currentResValue
            elif currentResName == 'h_rt':
                jobInfo["h_rt"] = currentResValue
            elif currentResName == 'h_data':
                jobInfo["h_data"] = currentResValue
            elif currentResName == 'h_vmem':
                jobInfo["h_vmem"] = currentResValue  
                
        # If job is started, add information from current job
        try:
            jobInfo["startDate"] = child[j].find('JAT_start_time').text
            
            resourcesUsed = child[i].find('JB_ja_tasks')[0].find('JAT_scaled_usage_list').findall('scaled')
            numResourcesUsed = len(resourcesUsed)
            
            for k in range(numResourcesUsed):

                currentUAname = resourcesUsed[k].find('UA_name').text
                currentUAvalue = resourcesUsed[k].find('UA_value').text

                if currentUAname == 'cpu':
                    jobInfo["cpu"] = currentUAvalue
                elif currentUAname == 'mem':
                    jobInfo["mem"] = currentUAvalue
                elif currentUAname == 'io':
                    jobInfo["io"] = currentUAvalue
                elif currentUAname == 'iow':
                    jobInfo["iow"] = currentUAvalue
                elif currentUAname == 'vmem':
                    jobInfo["vmem"] = currentUAvalue
                elif currentUAname == 'maxvmem':
                    jobInfo["maxvmem"] = currentUAvalue
                             
        except:
            jobInfo.update(startDate='NA', cpu='NA', mem='NA', io='NA', iow='NA', vmem='NA', maxvmem='NA')

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
