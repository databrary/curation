#!/bin/bash

PIXEL_FILE=$1
IMAGE_FILE=$2
SHADOW_FILE=$3
START_POINT=()
FIRST_PIXEL=false
do_not_collect=false

##
#loop through the text converted pixel output and pick out starting pixels for the each image
##

i=0
while read line; do
    if [[ $line == *000000* ]]
    then
        if [[ $do_not_collect == false ]]
        then
            echo "adding line"
            START_POINT[i]="$( cut -d':' -f 1 <<< "$line")"
            i=$(($i + 1))
            do_not_collect=true
        else 
            echo "not gonna add this"
        fi
    else
        do_not_collect=false
    fi
done < $PIXEL_FILE


##
#for each pixel point, we can run the extraction procedure
##

for e in "${!START_POINT[@]}"
do
    index="$e"
    pixel_val="${START_POINT[$e]}"
    red_single="red_$index_$IMAGE_FILE"
    sep_single="card_$index_$IMAGE_FILE"
    mask="mask_$index_$IMAGE_FILE"
    res_image="card_$index.png"

    convert "$SHADOW__FILE" -fill red -bordercolor white -draw "color "$pixel_val" filltoborder" "$red_single"
    convert "$red_single" -channel R -separate "$sep_single"
    convert "$red_single" "$sep_single" -compose subtract -threshold 50% -composite -morphology Dilate Square -negate "$mask"
    convert "$mask" "$IMAGE_FILE" -compose Screen -composite -trim "$res_image"
done


