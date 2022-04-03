# RPiTimeLapse

## A timelapse capture and viewing module for Raspberry Pi.

RPiTimeLapse is a collection of services handling the capture, rendering and display of timelapses. The capture service relies on Raspberry Pi's python camera library. A Flask web server hosts a user interface to slect the time period and then display a timelapse. The timelapse is rendered using a multithreaded opencv2 to ffmpeg pipeline to create a web-ready mp4 from the collected images. 

## Installation

RPiTimeLapse can be installed on a Raspberry Pi loaded with Raspbian.
Tested on a Pi 3 and Zero W

### Clone from GitHub and enter directory

    git clone https://github.com/marmig0404/rpitimelapse.git;
    cd rpitimelapse

### Install dependencies

    # some dependencies might take a while to build...
    sudo pip3 install -r requirements.txt

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