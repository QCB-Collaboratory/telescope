# Telescope test

This is an example to test if telescope is able to find your jobs on the remote server. The script ```generate_test.py``` performs repeated diagonalizations and writes the eigenvalues on a output file.

## Instructions to run this test

For simplicity, we will assume we are working on the server [hoffman2.idre.ucla.edu](https://idre.ucla.edu/hoffman2). Start by cloning this repository:
```shell
git clone https://github.com/QCB-Collaboratory/telescope
cd telescope
```
Use scp to copy the test script to your user account:
```shell
scp telescope/test/* hoffman2.idre.ucla.edu:~
```
This will copy these files on your home directory. You can change the location of those files, but for simplicity let's assume they remain on your home directory. Then, log in to your account on hoffman2 and run the following qsub command:
```
qsub -cwd -V -N tlscpTest -l h_data=1G,time=0:30:00 runTlscpTest.sh
```
This should submit a job identified as ```tlscpTest```. It should be queued at first, but eventually it will get started. This job should take no longer than 30 minutes. To check the status of that job from the command line, run from hoffman2 the following command:
```
qstat | grep tlscpTest
```
