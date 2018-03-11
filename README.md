# telescope

[![GPL Licence](https://badges.frapsoft.com/os/gpl/gpl.svg?v=103)](https://opensource.org/licenses/GPL-3.0/)
<img src="https://img.shields.io/badge/Python-_2.7,_3.*-brightgreen.svg">
[<img src="https://img.shields.io/badge/gitter_-_chat_online_-blue.svg">](https://gitter.im/unix-telescope/Lobby)

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



## License

Telescope is shared under the [GNU General Public License v3.0](https://github.com/QCB-Collaboratory/telescope/blob/master/LICENSE), please take a moment to read it. Permissions of this copyleft license are conditioned on making available complete source code of licensed works and modifications, which include larger works using a licensed work, under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights.

```
Telescope
Copyright (C) 2017  Thiago Schiavo Mosqueiro, QCB Collaboratory, et al

This material is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
```
