# Mistress - load testing tool for server-side applications
This distribution is **statistics server** component of Mistress.

## Setup
    sudo apt-get install libpq-dev python-dev libevent-dev libevent-2.0-5
    sudo apt-get install mercurial #for psycogreen from hg repo
    cd mistress-stat
    virtualenv --no-site-packages venv
    source venv/bin/activate
    pip install -r req.txt
    pip install -e .
    
    cp development.ini.example config.ini

## Usage
    cd mistress-stat
    source venv/bin/activate
    ./run config.ini

##License
[The MIT License](http://www.opensource.org/licenses/mit-license.php)
