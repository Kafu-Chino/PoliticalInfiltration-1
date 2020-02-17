#!/bin/bash
while ((1)); do
    hh=`date '+%H'`
    mm=`date '+%M'`
    ss=`date '+%S'`
    date
    if [ $hh -eq 0 -a $mm -ge 30 -a $mm -lt 40 ]
    then
        python position_task.py >> log/position_task.log &
        python activity_task.py >> log/activity_task.log &
        python emotion_task.py >> log/emotion_task.log &
        python social_task.py >> log/social_task.log &
        python influence_task.py >> log/influence_task.log &
        python word_daily_task.py >> log/word_daily_task.log &

        python topic_task.py >> log/topic_task.log &
        python domain_task.py >> log/domain_task.log &
        python political_task.py >> log/political_task.log &
        python word_analyze_task.py >> log/word_analyze_task.log &

        python personality_task.py >> log/personality_task.log &

        echo 'Finish excute python...______'
        date
        sleep 600
    else
        sleep 600
    fi
done