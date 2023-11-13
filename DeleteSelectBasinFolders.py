'''
BChoat 2023/11/10 env: genenv311

The hard drive on shared3 is full, so we need to open up some space.
This code looks through a csv file that has the catchments used in the study,
compares them to another file that has all 
'''



# %% import libraries
#####################################


import pandas as pd
from pathlib import Path
import shutil
from glob import glob



# %% define directories, files, vars, and such
########################################


# file with list of catchments to keep (not delete)
keep_list_file = 'C:/Projects/NOAA_NWM/DELETE_TESTS/AllBasins2023-10-021248.csv'

# file in which to save any relevant outputs/info
file_out = 'C:/Projects/NOAA_NWM/DELETE_TESTS/delete_logInfo.csv'

# directory in which to check to make sure the folder to be deleted already exists
# will also try comparing folder size, but if folders aren't identical this will not work
dir_check = 'C:/Projects/NOAA_NWM/MISCFiles'


# directory in which to remove folders that are not in keep_list_file
dir_del = Path('C:/Projects/NOAA_NWM/DELETE_TESTS')


# %% define function to get size of folder
######################

# %% read in data and work
#########################################

# create list to hold output notes and sizes of folders
notes_out = []
del_size = []
check_size = []

# read in file with list of files/folders to keep
df_filesKeep = pd.read_csv(keep_list_file)

# get list of folders to keep
list_keep = df_filesKeep['Folder_CAMELS'].to_list()

# loop through files/folders in dir_del and create list of folders
folders = [
    folder.name for folder in dir_del.iterdir() if folder.is_dir()
]

# id folders that do not appear in list_keep
folders_del = [
    folder for folder in folders if not folder in list_keep
]

# loop through folders_del and delete those folders
for f in folders:
    print(f)
    if f in folders_del:
        folder = f
        temp_del = Path(f'{dir_del}/{folder}')
        # get temp_del size
        temp_del_size = sum(f.stat().st_size for f in temp_del.rglob('*'))
        # check if folder is present in dir_check
        temp_check = Path(f'{dir_check}/{folder}')
        # if folder is present, get its size
        if temp_check.is_dir():
            temp_check_size = sum(f.stat().st_size for f in temp_check.rglob('*'))
            # check size against temp_del, if same then delete
            if temp_del_size == temp_check_size:
                shutil.rmtree(temp_del)
                notes_out.append('DELETED_Backed_Up_Same_Size')
                del_size.append(temp_del_size)
                check_size.append(temp_check_size)
            else: # otherwise, log notes and continue
                notes_out.append('NotDELETED_Backup_Not_Same_Size')
                del_size.append(temp_del_size)
                check_size.append(temp_check_size)
                continue
                
        else:
            # if not a folder that exists, then write to output log and continue
            notes_out.append('NotDELETED_Folder_Not_Backed_Up')
            del_size.append(temp_del_size)
            check_size.append(temp_check_size)
            continue

    else:
        notes_out.append('KEEP_FOLDER')
        del_size.append(temp_del_size)
        check_size.append(temp_check_size)



# write list of deleted folders to a csv file
df_deleted = pd.DataFrame({'Folders': folders,
                           'Notes': notes_out,
                           'WorkingSize': del_size,
                           'BackupSize': check_size})
df_deleted.to_csv(file_out, mode = 'a', index = False)

# %%
