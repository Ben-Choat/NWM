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
import os
from glob import glob



# %% define directories, files, vars, and such
########################################


# file with list of catchments to keep (not delete)
# keep_list_file = 'C:/Projects/NOAA_NWM/DELETE_TESTS/AllBasins2023-10-021248.csv'
keep_list_file = '/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen_Original/Calib_plots_WithNoah/AllBasins2023-10-021248.csv'

# file in which to save any relevant outputs/info
# file_out = 'C:/Projects/NOAA_NWM/DELETE_TESTS/delete_logInfo.csv'
file_out = '/home/bchoat/GITDIR/NWM/LogInfo_DeleteFiles.csv'

# directory in which to check to make sure the folder to be deleted already exists
# will also try comparing folder size, but if folders aren't identical this will not work
# dir_check = 'C:/Projects/NOAA_NWM/MISCFiles'
dir_check = '/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen_Original'


# directory in which to remove folders that are not in keep_list_file
# dir_del = Path('C:/Projects/NOAA_NWM/DELETE_TESTS')
dir_del = Path('/home/west/Projects/CAMELS/CAMELS_Files_Ngen')


# %% define function to get size of folder
######################

# %% read in data and work
#########################################

# create list to hold output notes and sizes of folders
notes_out = []
del_size = []
check_size = []
folders_out = []

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
try:
    for f in folders:
        print(f)
        if f in folders_del:
            print(f'{f} in folders_del')
            folder = f
            temp_del = Path(f'{dir_del}/{folder}')
            print(f'Current Dir: {temp_del}')
            # if ngen is present in temp_check, it is a symlink, so remove it
            # check up to two levels deep
            ngen_symlinks = [f'{temp_del}/ngen'] + \
                            list(glob(f'{temp_del}/*/ngen')) +\
                            list(glob(f'{temp_del}/*/*/ngen')) +\
                            list(glob(f'{temp_del}/*/*/*/ngen'))



            # remove ngen if id'd
            for symlink in ngen_symlinks:
                symlink = Path(symlink)
                # if symlink.is_symlink(): #  and not symlink.exists(): 
                if os.path.islink(symlink):
                   # symlink.unlink()
                   # shutil.rmtree(symlink)
                   os.unlink(symlink)

            print(f'ngen_symlinks ided and removed: {ngen_symlinks}')
           
            # get temp_del size
            temp_del_size = sum(f.stat().st_size for f in temp_del.rglob('*'))
            # check if folder is present in dir_check
            temp_check = Path(f'{dir_check}/{folder}')
            # if folder is present, get its size
            
            if temp_check.is_dir(): 
                temp_check_size = sum(f.stat().st_size for f in temp_check.rglob('*'))
                # check size against temp_del, if same then delete
#                if temp_del_size == temp_check_size:
                if temp_del_size <= temp_check_size:
                    shutil.rmtree(temp_del)
                    notes_out.append('DELETED_Backed_Up_Same_Size')
                    del_size.append(temp_del_size)
                    check_size.append(temp_check_size)
                    folders_out.append(f)
                else: # otherwise, log notes and continue
                    notes_out.append('NotDELETED_Backup_Not_Larger_Or_Equal')
                    del_size.append(temp_del_size)
                    check_size.append(temp_check_size)
                    folders_out.append(f)
                    continue
                    
            else:
                # if not a folder that exists, then write to output log and continue
                notes_out.append('NotDELETED_Folder_Not_Backed_Up')
                del_size.append('NA')
                check_size.append(temp_check_size)
                folders_out.append(f)
                continue

        else:
            print(f'{f} not in folders_del')
            notes_out.append('KEEP_FOLDER')
            del_size.append('NA')
            check_size.append('NA')
            folders_out.append(f)
except Exception as e:
    print('In exception')
    notes_out.append("exception_thrown")
    del_size.append('NA')
    check_size.append('NA')
    folders_out.append(f)
    # write list of deleted folders to a csv file
    df_deleted = pd.DataFrame({'Folders': folders_out,
                            'Notes': notes_out,
                            'WorkingSize': del_size,
                            'BackupSize': check_size})

    if Path(file_out).is_file():
        df_deleted.to_csv(file_out, mode = 'a', index = False, header = False)
    else:
        df_deleted.to_csv(file_out, index = False)


    raise e

# write list of deleted folders to a csv file
df_deleted = pd.DataFrame({'Folders': folders_out,
                        'Notes': notes_out,
                        'WorkingSize': del_size,
                        'BackupSize': check_size})

if Path(file_out).is_file():
    df_deleted.to_csv(file_out, mode = 'a', index = False, header = False)
else:
    df_deleted.to_csv(file_out, index = False)
