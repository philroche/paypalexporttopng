#!/bin/bash
for file in *.png
do
 # crop images using imagemagick
 convert -trim "$file" "$file"
 lp "$file"
done