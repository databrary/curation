#!/bin/bash

##
#This is pretty bare bones, run with FILE_PATH > OUT_PUT.csv to get a csv file of the creation and last modded dates of files
##

target="$1"
echo "FILE,FFPROBE_CREATED,STATTIME"
for file in "$target"/*
do
    base=`basename "$file"`
    if [[ -f $file && $base = *.* ]]; then
      FFPROBE=$(ffprobe -loglevel warning -show_format -of flat -i "$file" | grep '^format\.tags\.creation_time=')
      STAT=$(stat -c "%y" "$file")
      
      echo "\"$base\",${FFPROBE#*=},\"${STAT%.*}\""
      
    fi
  
done

