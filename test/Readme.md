Scp all files to a folder called telescope_test

Run on hoffman2:
```
qsub -cwd -V -N tlscpTest -l h_data=1G,time=6:10:00 runTlscpTest.sh
```
