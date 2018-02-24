create table jobs2(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user VARCHAR(30),
jobname TEXT,                 -- Unique job id
command TEXT,                 -- Command used to submit job
sourceDirectory TEXT,         -- Directory from which the job was submitted
outpath TEXT,                 -- Path and name for output file
path TEXT,                    -- Path to the script that is being run
memoryRequested TEXT,         -- Amount of memory requested
parallel INTEGER,             -- Running in parallel (1) or not (0)
cores INTEGER,                -- How many cores requested?
timeAdded VARCHAR(30),        -- When was this entry added to the database?
status INTEGER,               -- Current status of job (as of last time qstat was updated)
runTime TEXT,                 -- Time job has been running on Hoffman
timeRemaining TEXT,           -- Time remaining before job is killed by Hoffman
currentMemory INTEGER,        -- Memory currently in use by job
maximumMemory INTEGER,        -- Maximum memory used so far in job's history
HoffmanJobID INTEGER,         -- Job number given by Hoffman
HoffmanNode TEXT,             -- Node on which job was run
finalRunTime TEXT,            -- For finished jobs, how long did they run?
howEnded TEXT                 -- How did the job end? Completed, killed by user, killed by Hoffman, aborted?
);

insert into jobs2 (user,jobname, command,sourceDirectory , outpath, path, memoryRequested, parallel, cores, timeAdded, status, runTime, timeRemaining, currentMemory, maximumMemory, HoffmanJobID, HoffmanNode, finalRunTime, howEnded) values ('thmosque','test','ls -l ','/home/thmosque', '/home/thmosque', '/home/thmosque/out', '1GB', 1, 1, 'Fri Feb 23 16:08:42 PST 2018', 0, 0, '8:00:00', 0, 0, 988675, '78', 'NA', 'NA');
