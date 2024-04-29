#!/bin/bash

# BChoat 2024/04/15
# script to run serial NGEN jobs in parallel
# calls a python script that runs calibration
# in the python script min_ncat and max_ncat are input variables
# which are used to divide all HRUs by the number of cathcments
# in the HRU
# writes out process group IDs related to each python call so that
# all processes related to that call can be killed at once using:
# kill -- -$PGID
# replace $PGID with the associated PGID listed in logs/pgids.txt


# should scripts be executed after being created?
execute_scripts=true

# input list to divide runs by based on NCatchments
# On Shared3, there are 36 processors available
# e.g., if int_list=(0 5 10), then two calibration jobs will be executed, one running
# HRUs with 0 to 4 catchments, and the other with 5 to 9 catchments
# int_list=(0 5 10 15 20 25 30 35 40 45 50 60 70 80 90 100 110 130 150 175 200 225 250 300) 
# int_list=(0 15 30 40 50 60 70 75 80 85 90 97 101 104 108 109 120 125 130 135 153 155 157 180 190 195 200 203 205 225 235 250 268 280) 
# int_list=(0 5)
int_list=(0 3 6 9 12 15 18 21 24 27 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 150 250) 

mkdir -p logs

echo "execute_scripts=${execute_scripts}"

# Loop through the list, taking two values at a time
for ((i = 0; i < ${#int_list[@]} - 1; i++)); do
    # Extract two consecutive values from the list
    val_min=${int_list[i]}
    val_max=${int_list[i + 1]}

    echo "Running minNCat=${val_min} and maxNCat=${val_max}"

    # Create a new filename based on the two values
    new_filename="Run_calibration_BEC_${val_min}_${val_max}.py"

    # Copy the original Python file to the new filename
    cp Run_calibration_BEC.py "$new_filename"

    # Reiplace the values in the copied file
    sed -i "s/.*min_ncat = .*/min_ncat = $val_min/" "$new_filename"
    sed -i "s/.*max_ncat = .*/max_ncat = $val_max/" "$new_filename"

   # Check if Python scripts should be executed
   if [ "$execute_scripts" == true ]; then

	logfile="logs/${new_filename}.log"
	
        # Run the Python file in a new terminal window
	# NOTE: including '&' at the end allows the script to run in the background
	# while this one continues
        # sudo -S gnome-terminal -- /home/bchoat/Python/envs/genenv311/bin/python "$new_filename" &
	# gnome-terminal -- /home/bchoat/Python/envs/genenv311/bin/python "$new_filename" &

	# konsole --hold -e /home/bchoat/Python/envs/genenv311/bin/python "$new_filename" &
	# bash -c "/home/bchoat/Python/envs/genenv311/bin/python $new_filename" > "$logfile" 2>&1 &
	/home/bchoat/Python/envs/genenv311/bin/python "$new_filename" > "$logfile" 2>&1 &

	python_pid=$!
	# echo $python_pid

	# wait quick moment to ensure process is running
	sleep 0.2

	# get the PGID (process group ID) so can kill if needed)
	pgid=$(ps -o pgid= -p $python_pid)
	echo "PGID for this python call is: $pgid"
	echo "to kill all processes associated with python call, use 'kill -- -$pgid', where pgids, are listed here" >> "logs/pgids.txt"
	echo "${val_min} <= NCats < ${val_max}_PGID: ${pgid}" >> "logs/pgids.txt"
	# echo "Process Group ID (PIGD) - Kill using ... kill -- -$pgid ...: $pgid" >> "$logfile"


    fi
done

echo "Script files with modified values have been created."
