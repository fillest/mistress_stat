# Mistress - load testing tool for server-side applications
This distribution is **statistics server** component of Mistress.

## Setup
    sudo apt-get install libpq-dev python-dev libevent-dev libevent-2.0-5
    git clone https://github.com/fillest/mistress_stat
    cd mistress_stat
    virtualenv --no-site-packages venv
    source venv/bin/activate
    pip install -r req.txt
    pip install -e .
    sudo -u postgres createdb --echo --encoding=UTF8 --owner=postgres mistress
    
    cp development.ini.example development.ini
    #edit development.ini
    
    migrate development.ini
    create_user development.ini admin yourpassword admin

## Usage
    cd mistress_stat
    source venv/bin/activate
    ./run development.ini

##License
[The MIT License](http://www.opensource.org/licenses/mit-license.php)
