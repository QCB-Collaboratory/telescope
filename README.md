# telescope

[![GPL Licence](https://badges.frapsoft.com/os/gpl/gpl.svg?v=103)](https://opensource.org/licenses/GPL-3.0/)
<img src="https://img.shields.io/badge/Python-_2.7,_3.*-brightgreen.svg">


This is the awesome project we're on working today.


### Dependencies

* paramiko
* tornado


### Config file

You need to create a file name ```config.ini``` with the following format:
```
[CREDENTIALS]
USER   = <USERNAME>
SERVER = <SERVER ADDRESS>

[MONITOR]
NUMUSERS = 1
USER1 = <USERNAME>
```

By using the configuration file above, telescope will attempt to connect to the server by using ssh key pairs. If passwords are necessary, set your password as the second option in the CREDENTIALS group.
