#!/bin/bash

##
#This is pretty bare bones, run with FILE_PATH > OUT_PUT.csv to get a csv file of the creation and last modded dates of files
##

target="$1"
file_dot="."
echo "FILE,TIMEIN,TIMEOUT"
for file in "$target"/*
do
    if [[ "$(basename $file)" =~ "$file_dot" ]]; then
      TIMEIN=$(ffprobe -loglevel warning -show_format -of flat -i $file | grep 'format.tags.creation_time' | cut -d'=' -f 2)
      TIMEOUT=$(stat $file | grep "Modify: " | cut -d'.' -f 1 | sed "s/^Modify: //")
      
      echo "\"$(basename $file)\",$TIMEIN,\"$TIMEOUT\""
      
    fi
  
done

