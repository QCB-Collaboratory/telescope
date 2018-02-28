# Telescope test -- UCLA's hoffman2

This is an example to test if telescope is able to find your jobs on the remote server. For simplicity, we will assume we are working on the server [hoffman2.idre.ucla.edu](https://idre.ucla.edu/hoffman2). The script ```generate_test.py``` performs repeated diagonalizations and writes the eigenvalues on a output file.

** This is just a temporary test procedure while we continue to develop telescope further. ** If you're not in contact with developers, we don't recommend using telescope.


## Instructions start a test job on hoffman2

Start by cloning this repository:
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

## Running your local copy of telescope

To avoid providing your password to telescope, let's use ssh key pairs. We provide below instructions for Unix-based systems (including OSX). We need volunteers to test this on windows........

On your terminal, run (make sure to provide a password!)
```shell
ssh-keygen
```
Answer questions and save a pair. Let's assume the key is called ```id_rsa``` and it is located in the folder ```.ssh``` (recommended!). Then run
```shell
ssh-add .ssh/id_rsa
```
This adds the private key to your ssh-agent, which will use it automatically when logging to hoffman2. Next, let's copy your **public** key to hoffman2:
```shell
scp .ssh/id_rsa.pub <LOGIN>@hoffman2.idre.ucla.edu:./
```
Log in to hoffman2 and run:
```shell
mv id_rsa.pub .ssh/id_rsa.pub
cat .ssh/id_rsa.name.pub >> .ssh/authorized_keys
```
You are done. Log out of hoffman2 and you should already be able to log in without a password.

Back on your local machine, go back to the telescope folder. Go to the ```src``` folder:
```shell
cd src/
```
Create a file called config.ini with the following content:
```
[CREDENTIALS]
USER   = <USERNAME>
```
Finally, run
```shell
python telescope.py
```
Open a browser and access localhost:4000. You should see telescope on there.
