#!/bin/bash
#probably a one off script to check old eye tracker videos if they are upside down
#$1 is a newline delimited list of filepaths in a txt file
while read line
do
  if ffprobe -loglevel info $line 2>&1 | grep -q 'displaymatrix' ; then echo $line ; fi
done < $1