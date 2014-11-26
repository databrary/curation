#!/bin/bash

#convert meat.jpg -threshold 98% -morphology Dilate Octagon meat_0.png
#convert meat_0.png text: | grep -m 1 black | cut -d':' -f 1


##
#Input files
##

DIR=$1                          #./data/
IMAGE_FILE="$DIR$2"             #1.png

##
# Create first reference image
##

IMG_PREFIX="$(cut -d'.' -f 1 <<< $2)"            #1
IMG_REF="$(echo $DIR${IMG_PREFIX}_0.png)"        #1_0.png
convert "$IMAGE_FILE" -threshold 98% -morphology Dilate Square "$IMG_REF"

i=0

for n in {1..100}
do
    pixel_val="$(convert $IMG_REF text: | grep -m 1 000000 | cut -d':' -f 1)"
    IMG_RED="$(echo $DIR${IMG_PREFIX}_${i}_red.png)"
    IMG_MASK="$(echo $DIR${IMG_PREFIX}_${i}_mask.png)"
    IMG_SOLO="$(echo $DIR${IMG_PREFIX}_${i}_card.png)"
    convert "$IMG_REF" -fill red -bordercolor white -draw "color $pixel_val filltoborder" "$IMG_RED"
    i=$(($i + 1))
    IMG_REF=$(echo $DIR${IMG_PREFIX}_${i}.png)
    convert "$IMG_RED" -channel R -separate "$IMG_REF"
    convert "$IMG_RED" "$IMG_REF" -compose subtract -threshold 50% -composite -morphology Dilate Square -negate "$IMG_MASK"
    convert "$IMG_MASK" "$IMAGE_FILE" -compose Screen -composite -trim "$IMG_SOLO"

done




