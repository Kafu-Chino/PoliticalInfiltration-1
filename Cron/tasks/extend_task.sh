#!/bin/bash
while ((1)); do
    date
    nohup python extend_task.py &
    sleep 300
done