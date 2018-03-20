create table jobs(
jobId INTEGER PRIMARY KEY,    -- Unique job id
jobName TEXT,                 -- Name of the job
user VARCHAR(30),             -- Username
status INTEGER,               -- Current status of job (as of last time qstat was updated)
path TEXT,                    -- Path to the script that is being run
command TEXT,                 -- Command used to submit job
sourceDirectory TEXT,         -- Directory from which the job was submitted
outpath TEXT,                 -- Path and name for output file
memoryRequested TEXT,         -- Amount of memory requested
parallel INTEGER,             -- Running in parallel (1) or not (0)
cores INTEGER,                -- How many cores requested?
timeAdded VARCHAR(30),        -- When was this entry added to the database?
runTime TEXT,                 -- Time job has been running on Hoffman
timeRemaining TEXT,           -- Time remaining before job is killed by Hoffman
currentMemory INTEGER,        -- Memory currently in use by job
maximumMemory INTEGER,        -- Maximum memory used so far in job's history
clusterNode TEXT,             -- Node on which job was run
finalRunTime TEXT,            -- For finished jobs, how long did they run?
howEnded TEXT                 -- How did the job end? Completed, killed by user, killed by Hoffman, aborted?
);

--insert into jobs (jobId, jobName, user, status, path) values (1, 'test', 'username,'1', '/home/username');
