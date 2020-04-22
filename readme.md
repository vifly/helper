# Introduction
This script can download GitHub Releases and use repo-add (belong to Pacman) to create or update your Arch Linux local repository.

# Requirements
Python >= 3.6       
requests >= 2.23.0

# How to use
Clone or download this repository:
<pre>
    git clone git@github.com:vifly/helper.git
</pre>

There are two ways to install requirements, choose the one you like:
<pre>
    sudo pacman -S python-requests
</pre>
or      
<pre>
    # If you know Python venv
    python3 -m venv helper
    cd ./helper
    source ./bin/activate
    pip3 install -r requirements.txt
</pre>

Rename conf.py.example to conf.py, then edit conf.py according to comments.

Run:
<pre>
    python3 helper.py
</pre>

Tips: You can use [Cron](https://wiki.archlinux.org/index.php/cron) to run helper.py automatically.

# Arguments
<pre>
usage: helper.py [-h] [--force_download] [--no_update_repo]

optional arguments:
  -h, --help        show this help message and exit
  --force_download  Use it to force download releases when file is exist
  --no_update_repo  Just download releases, don't use repo-add to update Arch
                    local repository
</pre>