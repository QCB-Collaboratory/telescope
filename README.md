# telescope

This is the awesome project we're on working today.

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
