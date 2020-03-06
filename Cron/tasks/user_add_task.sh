#!/bin/bash
while ((1)); do
    date
    nohup python user_add_task.py &
    sleep 300
done