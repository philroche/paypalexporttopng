#!/bin/bash
for file in *.png
do
 # do something on $file
 convert -trim "$file" "$file"
 lp "$file"
done