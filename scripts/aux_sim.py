import json


def script_commands(simulator_settings):
    settings = json.dumps(simulator_settings).replace('"', '\\"')
    commands = f"""#!/bin/bash
    sudo apt update -y
    sudo apt install awscli -y
    sudo apt install python3-pip -y
    sudo apt --yes --no-install-recommends install apt-transport-https ca-certificates 
    wget --output-document=- https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - 
    sudo add-apt-repository "deb [arch=$(dpkg --print-architecture)] \
    https://download.docker.com/linux/ubuntu $(lsb_release --codename --short) stable"
    sudo apt update
    sudo apt -y --no-install-recommends install docker-ce
    sudo usermod --append --groups docker "$ubuntu"
    sudo systemctl enable docker
    sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    aws s3 cp s3://dell-artifacts/id_rsa ~/.ssh/id_rsa
    aws s3 cp s3://dell-artifacts/id_rsa ~/.ssh/id_rsa.pub
    chmod 600 ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa.pub
    ssh-keyscan bitbucket.org >> ~/.ssh/known_hosts
    cd /home/ubuntu/
    git clone git@bitbucket.org:emcbrasil/insper.pfe-intraday-trading.simulador.git
    cd insper.pfe-intraday-trading.simulador
    echo "{settings}" > simulator_settings.json
    pip3 install -r requirements.txt
    python3 simulator.py
    """
    """
    docker build -t martimfj/simulatrox .
    docker run martimfj/simulatrox
    """

    return commands


settings = {
    "date_init": "2019-10-25",
    "date_end": "2019-10-25",
    "settings": [
        {
            "strategy": "Mean_Reversion",
            "model": "0",
            "model_class": "Model_LSTM",
            "dependencies": [""],
            "instruments": ["AZUL4"],
        }
    ],
    "inserted_at": "2019-10-25T13:15:27.932Z",
    "name": "qualsdada",
    "tags": [""],
    "simulationId": "5db2f5710c38ebb056589356",
}


# https://www.google.com/search?sxsrf=ACYBGNQf6iDcTSX0tke3tQjSlySpOibkbg%3A1571987715385&ei=A6GyXYaiF8bC5OUP74uF8AQ&q=docker+pass+aws+credentials&oq=docker+pass+aws+&gs_l=psy-ab.3.0.0i203j0i22i30l2j0i8i13i30.3859.7264..8408...0.0..0.111.1615.5j11......0....1..gws-wiz.......35i39i19j35i39j0i67j0i131j0._K9YpTZfNek

