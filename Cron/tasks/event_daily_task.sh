#!/bin/bash
while ((1)); do
    hh=`date '+%H'`
    mm=`date '+%M'`
    ss=`date '+%S'`
    date
    if [ $hh -eq 0 -a $mm -ge 30 -a $mm -lt 40 ]
    then
        nohup python event_daily_task.py &

        echo 'Finish excute python...'
        date
        sleep 600
    else
        sleep 600
    fi
done