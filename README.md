# gsm-tool

get network clock and read incoming sms

# install

    sudo apt-get install python3-venv
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

# use

    source venv/bin/activate
    ./gsmtool.py --device /dev/ttyHS3 clock
