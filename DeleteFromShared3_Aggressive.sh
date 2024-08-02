#!/bin/bash

# BChoat 2024/05/08

# USE WITH CAUTION!!!!!!!!!!!!!!!!!!!!!!

# before, I deleted files and folders only if they matched exactly 
# the counterpart on the back up drive.
# we still have storage limitations on the local shared3 drive

# So, this script performs a much more agressive delete.
# If the file/folder is present in dir1 and dir2, and
# if the file/folder is not of size 0 on dir2, then it is 
# deleted from dir1.
# NOTE: the script does not look at subdiretories!!!!!!


# Define the paths to the directories
# dir1="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/TEST_BEN"
# dir2="/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen_Original/TEST_Ben"
dir1="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
dir2="/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen_Original/"


# define output file name that logs actions
logfile="Shared3AgressiveDelete_TEST_log.csv"

# create logfil
if [ ! -e "$logfile" ]; then
	echo "Item,Action" > "$logfile"
fi

echo "dir1 is $dir1, dir2 is $dir2" >> "$logfile"

# Iterate through each item in dir1
for item in "$dir1"/*; do
    # Extract the basename of the item
    item_name=$(basename "$item")

    # Check if the item exists in dir2
    if [ -e "$dir2/$item_name" ]; then
	
	# check if item is a directory and empty
	if [ -d "$dir2/$item_name" ] && [ -z "$(ls -A $dir2/$item_name)" ]; then
	    echo "$item_name, Not removed since empty in $dir2" >> "$logfile"

        # Check if the item in dir2 is a file and not empty
	# -s simply checks if size > 0, so not ensuring back up matches exactly
        elif [ -f "$dir2/$item_name" ] && [ ! -s "$dir2/$item_name" ]; then
	    echo "$item_name, Not removed since empty file in $dir2" >> "$logfile"
	
	else
            # Remove the item from dir1
            rm -rf "$item"
            echo "$item_name, Removed from $dir1" >> "$logfile"
           
        fi
    else
        echo "$item_name, No action since does not exist in $dir2" >> "$logfile"

    fi
done

