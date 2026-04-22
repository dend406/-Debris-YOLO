🚁 UAV Debris Detection System (YOLO + Raspberry Pi)
📌 Project Overview

This project presents a prototype of a UAV-based intelligent system for detecting debris of aerial targets using computer vision and deep learning.

The system is designed to support post-strike analysis and demining operations by automatically detecting potentially dangerous fragments and providing their geolocation in real time.

It combines:

onboard AI inference
GPS-based localization
IoT data transmission (MQTT)
edge computing on Raspberry Pi
🎯 Objectives
Develop a real-time object detection system using YOLO
Detect debris from UAV/rocket fragments in video streams
Geolocate detected objects using GPS
Transmit detection results to a ground station
Validate the system in near-real conditions
🧠 Technologies Used
YOLO (Ultralytics) – object detection
OpenVINO – model optimization for edge devices
OpenCV – video processing
MQTT (IoT protocol) – real-time communication
Python
Raspberry Pi 5
Raspberry Pi Camera v2
GPS Neo-6M
