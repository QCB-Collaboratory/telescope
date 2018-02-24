create table jobs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user VARCHAR(30),
jobname TEXT,
command TEXT,
outpath TEXT,
path TEXT,
created VARCHAR(30),
status INTEGER
);

insert into jobs (user,jobname, command, outpath, path, created, status) values ('thmosque','test','ls -l ', '/home/thmosque', '/home/thmosque/out', 'Fri Feb 23 16:08:42 PST 2018', 0);
