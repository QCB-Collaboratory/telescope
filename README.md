# telescope

[![GPL Licence](https://badges.frapsoft.com/os/gpl/gpl.svg?v=103)](https://opensource.org/licenses/GPL-3.0/)
<img src="https://img.shields.io/badge/Python-_2.7,_3.*-brightgreen.svg">
[<img src="https://img.shields.io/badge/gitter_-_chat_online_-blue.svg">](https://gitter.im/unix-telescope/Lobby)

Telescope is an open-source web applciation that tracks the progress of jobs submitted to remote servers using Sun Grid Engine (SGE) on-demand queueing system. It allows remote scheduling of pre-defined pipelines, as well as re-schedule queued jobs. Moreover, output files are rendered in HTML, allowing the use of markdown and rich-text features. Telescope operates using SSH key pairs that are stored after encrypted, and does not allow arbitrary code execution. Also, telescope does not assume anything from the remote server, it only assumes SSH connection.

This project was in great part developed during the [Winter Python Hackathon](https://github.com/QCB-Collaboratory/Python-Hackathon-Winter2018), at the [QCB Collaboratory](https://qcb.ucla.edu/collaboratory/), UCLA.

### Dependencies

Telescope can be self-host and track jobs from a list of users. It runs in Python 2.7\* or 3\*, with the following non-standard dependencies:

* paramiko
* tornado
* xml.etree.ElementTree
* configparser



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
