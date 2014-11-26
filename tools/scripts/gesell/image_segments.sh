#!/bin/bash

##
#Input files
##

DIR=$1                          
IMAGE_FILE="$DIR$2"             

##
# Create first reference image
##

IMG_PREFIX="$(cut -d'.' -f 1 <<< $2)"            
IMG_REF="$(echo $DIR${IMG_PREFIX}_0.png)"        #1_0.png
convert "$IMAGE_FILE" -bordercolor White -border 10x10 "$IMAGE_FILE"
convert "$IMAGE_FILE" -threshold 95% -morphology Dilate Square "$IMG_REF"

i=0

##
# loop and use successive reference images, removing the ones already used
## 

pixel_val="$(convert $IMG_REF text: | grep -m 1 000000 | cut -d':' -f 1)"

while [[ -n "$pixel_val" ]]
do
    convert "$IMG_REF" -median 5 "$IMG_REF" #clear out small patches of pixels - though removes some details from images
    pixel_val="$(convert $IMG_REF text: | grep -m 1 000000 | cut -d':' -f 1)" 
    echo "pixel value is now: $pixel_val"
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




