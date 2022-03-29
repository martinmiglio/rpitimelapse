# RPiTimeLapse

A timelapse capture and viewing module for raspberry pi

## Installation

### Clone from GitHub and enter directory

    git clone https://github.com/marmig0404/rpitimelapse.git;
    cd rpitimelapse

### Install dependencies

    sudo apt install libatlas3-base libgfortran5
    sudo pip3 install numpy==1.21.4 imageio

### Setup systemd services

    sudo cp systemd/* /etc/systemd/system; # move service files
    sudo systemctl daemon-reload;
    # enable services for auto-start
    sudo systemctl enable tlcamera.service tlwebviewer.service;
    # start services now
    sudo systemctl start tlcamera.service tlwebviewer.service;
    # check service status
    sudo systemctl status tlcamera.service tlwebviewer.service

## Update

### Pull from GitHub

    git pull
  
### Update services

    sudo systemctl restart tlwebviewer tlcamera