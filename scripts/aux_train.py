import json

def script_commands(simulator_settings):
    settings = json.dumps(simulator_settings).replace('"', '\\"')
    commands = """#!/bin/bash
    sudo apt update -y
    sudo apt install awscli -y
    sudo apt --yes --no-install-recommends install apt-transport-https ca-certificates 
    wget --output-document=- https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - 
    sudo add-apt-repository "deb [arch=$(dpkg --print-architecture)] \
    https://download.docker.com/linux/ubuntu $(lsb_release --codename --short) stable"
    sudo apt update
    sudo apt -y --no-install-recommends install docker-ce
    sudo usermod --append --groups docker "$USER"
    sudo systemctl enable docker
    sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    aws s3 cp s3://dell-artifacts/id_rsa ~/.ssh/id_rsa
    aws s3 cp s3://dell-artifacts/id_rsa ~/.ssh/id_rsa.pub
    chmod 600 ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa.pub
    ssh-keyscan bitbucket.org >> ~/.ssh/known_hosts
    cd /home/ubuntu/
    git clone git@bitbucket.org:emcbrasil/insper.pfe-intraday-trading.treinamento.git
    cd insper.pfe-intraday-trading.simulador
    echo "{settings}" > trainer_settings.json	
    """
    """
    Cria shell scrip para baixar as dependências do Simulador:
        - Update
        - Install Docker
            - Pandas
            - Boto3
            - Numpy
            - Fastparquetss
        - Clone Repo
        - Docker run file

    """

    # sudo apt install python3-pip -y
    # pip3 install pandas boto3 numpy fastparquet

    return commands

