# VIDEO HARD CUT DETECTION APPLICATION
 This repository contains flask application for detecting hard cuts in videos. A hard cut is a sudden change in the video stream, such as when a new scene begins. This code can be used to detect hard cuts in videos for a variety of purposes, such as video editing, video analysis, and video search.

The code is written in Python and uses the OpenCV library. It has a user-friendly interface and can be run on any computer with Python installed.

## FLASK APPLICATION
This Flask application is versatile and can be used both locally within a virtual environment and deployed to a server. Whether you want to run it on your local machine for testing and development purposes or deploy it to a production server for wider access, this application is capable of meeting your needs.

## TESTING
To use the code, simply clone this repository then create a virtual environment

```
$ pip install virtualenv
$ virtualenv -p /usr/bin/python3.10.7 virtualenv_name

```
start the virtual environment
```
$ cd <envname>
$ Scripts\activate
$ pip install -r requirements.txt
```
then run
```
Python app2.py
```
you will see the server running
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.0.7:5000
```
click on anyone link and you will see the website open in for default browser

## EXAMPLE
An example video and its output has been included for reference

 **_NOTE:_**  It's important to note that video processing can be resource-intensive and may slow down your system, especially for longer videos or lower-end hardware configurations. Please be patient while the application processes the video.
#### For reference (**10min video(720p)** takes 20 min on intel i5 11th gen with 16gb ram)
