########!/usr/bin/env python3

'''
BChoat ~2024/01/10

Cleaning/updating code previously created by L.Cunha.

This script expects to be executed from an environment containing
each of the imported libraries. For example, when I run it I use:
    sudo /home/bchoat/Python/envs/genenv311/bin/python NameOfThisFile.py

'''

import sys
import os
import subprocess
import time
import yaml
import io
import pandas as pd
import json
import shutil 
import glob
import geopandas as gp
from datetime import datetime

NextGen_folder = "/home/west/git_repositories/ngen_20231213_calib/ngen"
print(f'Using NGEN install located in: {NextGen_folder}')

# Define which python to use when calling subprocess.call(python ...) - BChoat
python_use = f"{NextGen_folder}/venv/bin/python"
# define path to activate, which is used to activate a venv env.
# activate_use = f"{NextGen_folder}/venv/bin/activate"

# BChoat: this folder is not used anywhere??
# calib_output_folder="calibSep_PET_NC"

# ngen-cal/python/ngen_conf/src/ngen/config has .py files for each model that 
# can be claibrated, including variable mappings
# Next_gen_library="/home/west/git_repositories/ngen-cal/python/ngen_conf/src/ngen/config/"

# Forcing variable is used to update Realization templates and to 
# move files as needed
Forcing="NetCDF" # NEed to adapt realization and ngen-cal code

# set number of iterations for using TOPMODEL and CFE/CFE_X
# NOTE: ngen-cal requires number of iterations to be >= 2
tm_iterations = 2 # 120
cfe_iterations = 2 # 300

# set the minimum number of nexuses that must be present for a job to run
# BChoat, 2024/1/10
# in earlier versions, hdf5 file was not produced if < 2 nexuses were present.
# so for first round of calibrations there was required to be >= 2 nexuses.
# We may test if this has been fixed later. If so, we can add basins.
min_nexuses = 2

# BChoat: I don't think this chunk of code editing the default provider is 
# necessary either since the realization file specifies the provider
#file_to_modify=Next_gen_library+"configurations.py"
#if(Forcing=="CSV"): 
#    str_sub="sed -i 's/Provider.NetCDF/Provider.CSV/g' " +  file_to_modify
#    out=subprocess.call(str_sub,shell=True) 
#if(Forcing=="NetCDF"): 
#    str_sub="sed -i 's/Provider.CSV/Provider.NetCDF/g' " +  file_to_modify
#    out=subprocess.call(str_sub,shell=True)



Hydrofabrics_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
# Select_calibration_file="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/SelectModelCal/CAMELS_v3_calib_BestModels.csv"
# Best_PET=pd.read_csv(Select_calibration_file,dtype={'hru_id_CAMELS': str})
# Best_PET=Best_PET.set_index(['hru_id_CAMELS'])
# Best_PET=Best_PET['A_Best1']


Hydrofabrics_folder_HD="/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/"
# Select_calibration_file="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/Select_calibration_HLR_RFC.csv"
# Selected_calibration=pd.read_csv(Select_calibration_file,dtype={'hru_id_CAMELS': str})
# Selected_calibration=Selected_calibration.set_index(['hru_id_CAMELS'])
# Selected_calibration = Selected_calibration[~Selected_calibration.index.duplicated(keep='first')]

Select_calibration_file="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_calib_BestModelsAll.csv"
ALL=pd.read_csv(Select_calibration_file,dtype={'hru_id_CAMELS': str})
ALL=ALL.set_index(['hru_id_CAMELS'])
ALL=ALL.rename(columns={'N_Nexus':'N_nexus'})
ALL=ALL.drop(['Q_Best_Topmodel','Q_Best_CFE_X'],axis=1).dropna()

#Selected_calibration=pd.concat([Selected_calibration,ALL['A_Best1']],axis=1)
#Selected_calibration=Selected_calibration.dropna()

Selected_calibration=ALL.copy()
# set up environment to enable everything to be ran - west/anaconda3/bin used for t-route - BChoat
# troubleshooting - BChoat
os.environ['PATH']=NextGen_folder+"/venv/bin:/usr/bin:"
# :"+"/home/west/TauDEMDependencies/mpich/mpich-install/bin:/home/west/anaconda3/bin:/home/west/anaconda3/condabin:/sbin:/bin:/usr/bin:/usr/local/bin:/snap/bin"+":"
# os.environ['PATH']="/home/bchoat/Python/envs/NWMenv39/bin:"+"/home/west/TauDEMDependencies/mpich/mpich-install/bin:/home/west/anaconda3/bin:/home/west/anaconda3/condabin:/sbin:/bin:/usr/bin:/usr/local/bin:/snap/bin"+":"

# BChoat - ngen still not finding python 3.8, so editing ld_LIBRARY_PATH here
# library_path = '/snap/gnome-3-38-2004/140/usr/lib/x86_64-linux-gnu'
# os.environ['LD_LIBRARY_PATH'] = f'{library_path}:{os.environ.get("LD_LIBRARY_PATH", "")}'
#PATH=$HOME/TauDEMDependencies/mpich/mpich-install/bin:$PATH ; export PATH

# define directory holding template configuration files
# (e.g., Realization... and calib_config files)
calib_config_dir="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/calib_conf/"

# Why is this here - what does it do?
# os.environ['HDF5_DISABLE_VERSION_CHECK']="1"


# LKC - to implement
# param_to_remove=[] 

start_time="2008-10-01 00:00:00"
# end_time="2013-10-01 00:00:00"
end_time = "2009-10-01 00:00:00" # bchoat troubleshooting

# BChoat - focus on Topmodel,  but run others t comare results
# Rainfall_Runoff_ModelAr=["CFE","CFE_X","Topmodel"]
Rainfall_Runoff_ModelAr=['Topmodel']
# Rainfall_Runoff_ModelAr=["CFE"]
NG_NotRunning=pd.DataFrame()

#First SElection 
# Selected_calibration[(Selected_calibration['frac_snow']<0.1) & (Best_PET.str.contains('PET')) & (Selected_calibration['N_nexus']>=2)].sort_values(by='N_nexus')[['NCat','N_nexus']]
# Selected_calibration=Selected_calibration[(Selected_calibration['frac_snow']<0.1) & (Best_PET.str.contains('PET')) & (Selected_calibration['N_nexus']>=2)]
# Selected_calibration=Selected_calibration.sort_values(by="NCat")

#Second SElection

#Selected_calibration=Selected_calibration[(Selected_calibration['A_Best1'].str.contains('NOAH')) & (Selected_calibration['N_nexus']>=2)]
#Selected_calibration=Selected_calibration.sort_values(by="NCat")

#All Values selection

# Do_not_run=Selected_calibration[(Selected_calibration['frac_snow']>0.1) & (Selected_calibration['A_Best1'].str.contains('PET'))]

# Selected_calibration=Selected_calibration[((Selected_calibration['frac_snow']<0.1) & (Selected_calibration['A_Best1'].str.contains('PET'))) 
#                                           | ((Selected_calibration['frac_snow']>0.1) & (Selected_calibration['A_Best1'].str.contains('NOAA')))]

#Selected_calibration=Selected_calibration[(Selected_calibration['A_Best1'].str.contains('NOAH'))]

#Selected_calibration=Selected_calibration[(Selected_calibration['A_Best1'].str.contains('PET')) & (Selected_calibration['frac_snow']>=0.1)]
#Selected_calibration=Selected_calibration.sort_values(by="NCat")
Done=[]
count=0
run=0
idd=[]

# Priority_file='/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Calib_plots_Primary/AllBasins2022-11-291248.csv'
Priority_file = '/home/west/Projects/CAMELS/CAMELS_Files_Ngen/ForPaper/AllBasins2023-03-141248.csv'
Priority=pd.read_csv(Priority_file,dtype={'hru_id_CAMELS': str})
Priority=Priority.set_index(['hru_id_CAMELS'])
Priority=Priority.dropna()

# BChoat - Editing to run any catchment that previously had output for CFE or CFE_X
# this is because we want to run the same catchments for topmodel, that have
# previously been ran for CFE and/or CFE_X
Priority=Priority[(Priority['CFE']==1) | (Priority['CFE_X']==1)]
#Priority=Priority[(Priority['CFE']==1) | (Priority['CFE_X']==1) | (Priority['Topmodel']==1)]
#Priority['Sum']=Priority['CFE']+Priority['CFE_X']+Priority['Topmodel']
#Priority=Priority[Priority['Sum']==1]
#Priority=Priority[(Priority['Sum']>=2)]

# BChoat: we only want to run HRUs that were previously ran for CFE, so subset to those catchments
Selected_calibration=Selected_calibration.loc[Priority.index.values]
Selected_calibration=Selected_calibration.sort_values(by="NCat")
try:
    Selected_calibration=Selected_calibration.drop('04197170')
except:
    pass

# Priority_file="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/Calib_priority_10312022.shp"
# Priority = gp.read_file(Priority_file,dtype={'hru_id_CAMELS': str})
# Selected_calibration=Selected_calibration.loc[Priority.hru_id_CAM.values]
# 10: runs for basins we have other models ran
# 11: runs for basins we have other models ran

# Run in 20: Selected_calibration=Selected_calibration.loc[['08050800','08267500','06479215']]
# Run in 21:
#Selected_calibration=Selected_calibration.loc[['08050800']]

# Run in 22: 
#Selected_calibration=Selected_calibration.loc[['04115265','04063700','06479215','07195800']]

# Run in 23: 
#Selected_calibration=Selected_calibration.loc[['09306242','08050800','08066300','08103900']]

# Run in 24: 
#Selected_calibration=Selected_calibration.loc[['08267500','01073000','06803510']]

# Rn in 25
#Selected_calibration=Selected_calibration.loc[['08267500']]
#file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode

#Selected_calibration=Selected_calibration.loc[['05458000']]
#C78: 0-30
#C79: 30-35
#C80: 35-40
#C81: 40-45

#################
# str_sub="source "+NextGen_folder+"/venv/bin/activate"
# str_sub = f"source {activate_use}"
#                    out=subprocess.call(str_sub,shell=True)
                    # ensure subprocess inherits from current env
# out = subprocess.call(str_sub, shell = True, env = os.environ, executable = '/bin/bash')
# subprocess.call(str_sub, shell = True, env = os.environ, executable = '/bin/bash')

# print current python as sanity check
which_py = subprocess.check_output('which python', shell = True)
which_py = which_py.decode('utf_8').strip()

print(f'\n\nWhich Python: {which_py}\n\n')

# str_sub = 'pip install "git+https://github.com/Ben-Choat/ngen-cal@devBranch#egg=ngen_cal&subdirectory=python/ngen_cal"' 
# subprocess.call(str_sub, shell = True)

##################
## BChoat - Troubleshooting
#print('\nAbout to run test realization directly\n\n')
#
#
# Uncomment this chunk to run test. NOTE that if Realization being used as 
# empty model_params:{}, then this will fail. THis may be case since 
# template realizations have empty model_params:{}
#os.chdir('/home/west/Projects/CAMELS/CAMELS_Files_Ngen/camels_10259000_22592131')
#
## str_sub="cp -rf /home/west/Projects/CAMELS/CAMELS_Files_Ngen/t-route ."  
## out=subprocess.call(str_sub,shell=True) 
#str_sub="cp /home/west/Projects/CAMELS/CAMELS_Files_Ngen/calib_conf/Realization_noahowp_cfe_calibNC.json ."  
#out=subprocess.call(str_sub,shell=True)  
#
#
## run job w/o ngen-cal to test - BChoat
#str_sub = '/home/west/Projects/CAMELS/CAMELS_Files_Ngen/camels_10259000_22592131/ngen/cmake_build/ngen \
#        /home/west/Projects/CAMELS/CAMELS_Files_Ngen/camels_10259000_22592131/spatial/catchment_data.geojson "all" \
#        /home/west/Projects/CAMELS/CAMELS_Files_Ngen/camels_10259000_22592131/spatial/nexus_data.geojson "all" \
#        Realization_noahowp_cfe_calibNC.json'
#
#subprocess.call(str_sub, shell = True)
#print(f'Just ran \n {str_sub} in \n{os.getcwd()}\n\n')
#^^^^^^^^^^^^^^^^^^^^^^^^^^^
########################



#BEN: Recommend changing to 1 and running in parallel 
Parallel_run=0
flag_obj="kling_gupta"
if(flag_obj=="nnse"):
    str_obj="nnse"
    
elif(flag_obj=="kling_gupta"):
    str_obj=""
    
else:
    print("No objective defined" )
# for i in range(0,len(Selected_calibration)):
for i in range(0, 1):
# for i in range(0, 3):
    Folder_CAMELS=Selected_calibration.iloc[i]['Folder_CAMELS']
    hru_id=Selected_calibration.index[i]
    parallel_flag=0
    if(Selected_calibration.iloc[i]["NCat"]>=12) & (Parallel_run==1):
         # set up partition file for running in parallel - BChoat
        parallel_flag=1
        if(Selected_calibration.iloc[i]["NCat"]<=18):  partition=2
        elif(Selected_calibration.iloc[i]["NCat"]>18) & (Selected_calibration.iloc[i]["NCat"]<=32) :  partition=1
        elif(Selected_calibration.iloc[i]["NCat"]>32) & (Selected_calibration.iloc[i]["NCat"]<48) :  partition=8
        else:  partition=16
        
        
    # BChoat - editing this from range(0, 3), so that it auto-adjusts to number of values in Rainfall_Runoff_ModelAr    
#     for j in range(0,3):
    for j in range(0, len(Rainfall_Runoff_ModelAr)):
        # runs failed when N_nexus == 1, so skip if that is the case - BChoat
        if(Selected_calibration.iloc[i]['N_nexus']<2):
        #if(Selected_calibration.iloc[i]['frac_snow']>0.1) & ('PET' in Selected_calibration.iloc[i]['A_Best1']):
            print("Not running, N_nexus < 2 "+Folder_CAMELS)
        else:
         
            run=run+1
            idd.append(i)

           
            #PET=Best_PET.loc[hru_id]
            PET=Selected_calibration.iloc[i]['A_Best1']
            #BEN: Do not worry about this, this was test, but can leave for now
            if(hru_id=='02430085') & (hru_id=='02465493'):
                PET="PET_4"
            flag_NOAH_PET=0
            
            #PET="NOAH"
            # if best pet function is PET1 through PET5 and fraction snow > 0.1, then set NOAH_PET
            # flag to 1, so that snow melt is incorporatied (via NOAH)
            if("PET" in PET) & (Selected_calibration.iloc[i]['frac_snow']>0.1):
                flag_NOAH_PET=1
            #PET="PET_4"
            # Modify function in calibration to pass the write info

            
            Rainfall_Runoff_Model=Rainfall_Runoff_ModelAr[j]
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            str_log="Collecting params for,"+hru_id+","+dt_string+","+PET+","+Rainfall_Runoff_Model+"\n"
            file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
            file1.write(str_log)    
            file1.close()
            
            #################################### BChoat
            # BCHOAT: I'm not sure this is necessary since I've manually edited those files as 
            # I've identified as being necessary, and we provide variable mappings in Realization files

            # Variable Mapping
            # May need to give attention here based on updated files in ngen-cal
            # Depending on if cfe or topmod, modify variable map for BMI communication
            # edits code at /ngen-cal/python/ngen_conf/src/ngen/config
            # edits are made to ensure model from which 
#            if(Rainfall_Runoff_Model=="CFE"):file_to_modify=Next_gen_library+"cfe.py"
#            else: file_to_modify=Next_gen_library+"topmod.py"
#    
#            # if best function is PET1 through PET5
#            if("PET" in PET):
#                str_var="_variable_names_map =  {\n        \"atmosphere_water__liquid_equivalent_precipitation_rate\": \"atmosphere_water__liquid_equivalent_precipitation_rate\"\n        }" 
#                if(flag_NOAH_PET==1):
#                    str_var="_variable_names_map =  {\n        \"atmosphere_water__liquid_equivalent_precipitation_rate\": \"QINSUR\"\n        }" 
#            else: str_var="_variable_names_map =  {\n        \"water_potential_evaporation_flux\": \"EVAPOTRANS\",\n        \"atmosphere_water__liquid_equivalent_precipitation_rate\": \"QINSUR\"\n        }"   
#      
#                    # Open a file: file
#            file = open(file_to_modify,mode='r')
#            all_of_it = file.read()
#            file.close()
#            index=all_of_it.find("_variable_names_map")
#            final=all_of_it[0:index]+str_var
#            with open(file_to_modify, 'w') as f:
#                f.write(final)
            #########################################################

            #PET="PET_4"
            # output is placed in directory in which it was executed, so we define
            # work_dir to always be in the catchment folder for which we are simulating
            work_dir=Hydrofabrics_folder+Folder_CAMELS+"/"
            work_dir_HD=Hydrofabrics_folder_HD+Folder_CAMELS+"/"
            
            os.chdir(work_dir)
            
            ##########################################################
            # Set calibration configuration file (e.g., range of values, objective funct, method)
            # modify template file for specific case
            if(Rainfall_Runoff_Model=="CFE"): 
                calib_config_base=calib_config_dir+"/calib_config_CAMELS_CFE_Calib_Sep_2.yaml"
                iterations=cfe_iterations # 300 
            elif(Rainfall_Runoff_Model=="CFE_X"): 
                calib_config_base=calib_config_dir+"/calib_config_CAMELS_CFE_X2_Calib_Sep_2.yaml"
                iterations=cfe_iterations# 300 
            elif(Rainfall_Runoff_Model=="Topmodel"): 
                calib_config_base=calib_config_dir+"/calib_config_CAMELS_Topmodel_Calib_Sep_2.yaml"
                iterations=tm_iterations#120
            else: print("error: model does not exist")
            ##########################################################
            # Realization file for ngen
            # modify template for specific case
            if('PET' in PET) & (Selected_calibration['frac_snow'].iloc[i]<0.1):  
                if(Rainfall_Runoff_Model=="CFE"): calib_realiz_base=calib_config_dir+"Realization_pet_cfe_calibNC.json"
                elif(Rainfall_Runoff_Model=="CFE_X"): calib_realiz_base=calib_config_dir+"Realization_pet_cfe_X_calibNC.json"
                elif(Rainfall_Runoff_Model=="Topmodel"): calib_realiz_base=calib_config_dir+"Realization_pet_Topmodel_calibNC.json"
                else: print("error: model does not exist")

                # modify PET method in calibration config files (within individual catchment folder)
                PET_Type=int(PET.split("_")[1])
                for ii in range(1,6):
                    Run_sed="sed -i 's/pet_method="+str(ii)+"/pet_method='"+str(PET_Type)+"'/g' ./PET/*"
                    out=subprocess.call(Run_sed,shell=True)  
                    
            elif('PET' in PET) & (Selected_calibration['frac_snow'].iloc[i]>=0.1):
                if(Rainfall_Runoff_Model=="CFE"): calib_realiz_base=calib_config_dir+"Realization_noahowp_pet_cfe_calibNC.json"
                elif(Rainfall_Runoff_Model=="CFE_X"): calib_realiz_base=calib_config_dir+"Realization_noahowp_pet_cfe_X_calibNC.json"
                elif(Rainfall_Runoff_Model=="Topmodel"): calib_realiz_base=calib_config_dir+"Realization_noahowp_pet_Topmodel_calibNC.json"
                else: print("error: model does not exist")
 
                # modify PET method in calibration config files (within individual catchment folder)
                PET_Type=int(PET.split("_")[1])
                for ii in range(1,6):
                    Run_sed="sed -i 's/pet_method="+str(ii)+"/pet_method='"+str(PET_Type)+"'/g' ./PET/*"
                    out=subprocess.call(Run_sed,shell=True)            
            else:
               if(Rainfall_Runoff_Model=="CFE"): calib_realiz_base=calib_config_dir+"Realization_noahowp_cfe_calibNC.json"
               elif(Rainfall_Runoff_Model=="CFE_X"): calib_realiz_base=calib_config_dir+"Realization_noahowp_cfe_X_calibNC.json"
               elif(Rainfall_Runoff_Model=="Topmodel"): calib_realiz_base=calib_config_dir+"Realization_noahowp_Topmodel_calibNC.json"  
               else: print("error: model does not exist")
               PET="NOAH"
            Model=PET+"_"+Rainfall_Runoff_Model    
            
            # BChoat - trying a change to see if results are written (that are currenlty not)

            # calib_folder=work_dir+Model+str_obj+"/"
            # calib_folder=work_dir+"/"+Model+str_obj+"/"
            
            # BChoat - trying a change to see if results are written (that are currently not)

            # calib_folder_HD=Hydrofabrics_folder_HD+"/Results/"+Folder_CAMELS+"/Calibration/"+Model+"/" +Model+str_obj+"/"
            calib_folder_HD=Hydrofabrics_folder_HD+"Results/"+Folder_CAMELS+"/Calibration/"+Model+"/" +Model+str_obj+"/"

            #calib_folder_HD=Hydrofabrics_folder_HD+"/Results/"+Folder_CAMELS+"/Calibration/"+PET+"_"+Rainfall_Runoff_Model+"/" 

            # troubleshooting -BChoat
            # print(f'\n\ncalib_folder: {calib_folder}\n')
            print(f'\n\ncalib_folder_HD: {calib_folder_HD}\n\n')
            

            ########################################
#            if os.path.exists(calib_folder_HD):
#                str_sub = f'rm -r {calib_folder_HD}'
#                out = subprocess.call(str_sub, shell = True)
#            if(not os.path.exists(calib_folder_HD)): os.makedirs(calib_folder_HD)
            # BChoat - trying a change to see if results are written (that are currenlty not)
#            objective_log = calib_folder_HD+'/ngen-calibration_objective.txt'    
            # objective_log = calib_folder_HD+'ngen-calibration_objective.txt'    

            # define objective log location/name on exertnal hard drive to see if it exists
            objective_log_HD = f'{calib_folder_HD}objective_log.txt'
            # define for local drive as well for checking/removing later
            # objective_log = f'{calib_folder}objective_log.txt'

            # troubleshooting - BChoat
#             print(f'\nobjective_log: {objective_log}')
            print(f'\nobjective_log_HD: {objective_log_HD}\n\n')                  


            # BChoat: I'm not sure the purpose of this chunk of code so I am commenting it out
            # and rewriting this portion to check if the objective file already exists in
            # external hard drive. If so, read in size of file which is used later in code &
            # check number of iterations in the file. If number of iterations is smaller than
            # expected, then set size = 0.
            # Then below, if file is smaller than expected, then it is assumed the previous execution
            # did not complete as expected, so it is reran.
            # In that case, the small objective file will be overwritten when the new objective
            # is copied to external hard drive.
            if(os.path.exists(objective_log_HD)):
                print('\nobjective_log.txt exists on external harddrive\n')
                Objective = pd.read_csv(objective_log_HD, header = None)
                if len(Objective) < iterations-1:
                    print(f'\nLength of objective file is shorter than expected.\
                            ({len(Objective)} lines.')
                    # print(f'Rerunning {Folder_CAMELS} {Rainfall_Runoff_Model}\n')
                    size = 0
                else:
                    print('\n\n-----------------------------')
                    print(f'{objective_log_HD}')                    
                    print('already exists and is the correct length, so going to next HRU')
                    print('-----------------------------\n\n')
                    continue
                    # size = os.path.getsize(objective_log)

            
                        

            #str_sub="rm -rf "+calib_folder
            #out=subprocess.call(str_sub,shell=True)
#            print(str(i) + " " + Model+ " " +Folder_CAMELS)
#             if((os.path.exists(objective_log))): 
#                 print("File exists in HD ")
#                 print(f'{objective_log} exists in {calib_folder}')
#                Objective = pd.read_csv(objective_log,header=None)
#                size=os.path.getsize(objective_log)
#                print("File Exist " + Folder_CAMELS + " "+str(size) + " " + PET)
#                if(len(Objective)<iterations-1):
#                    print("Not Enought iterations in HD ")
#                    #print("Run" + Folder_CAMELS + " ""+Rainfall_Runoff_Model") 
#                    size=0
#            else:
                #BChoat - Comment out these lines since they are redundant with the previous lines
#                 objective_log = calib_folder_HD+'/ngen-calibration_objective.txt' 
#                 if((os.path.exists(objective_log))):
#                     print("File exists in HD ")
#                     Objective = pd.read_csv(objective_log,header=None)
#                     size=os.path.getsize(objective_log)
#                     print("File Exist " + Folder_CAMELS + " "+str(size) + " " + PET)
#                     if(len(Objective)<iterations-1):
#                         print("Not Enought iterations in HD ")
#                         #print("Run" + Folder_CAMELS + " ""+Rainfall_Runoff_Model") 
#                         size=0
#                 else:
#                  print("File does not exist\n")
#                 size=0
#            print("\n")
            ##########################################
            #if(size==0):   
            #if(Selected_calibration.iloc[i]['N_nexus']>=2) & (size<100):
            # BChoat troubleshooting
            if(Selected_calibration.iloc[i]['N_nexus']>=min_nexuses): # & (size<100):
                print("Run " + Folder_CAMELS ) 
                print(f'Run {Folder_CAMELS}')
                             
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    str_log="Starting running calibration,"+hru_id+","+dt_string+"\n"
                    file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
                    file1.write(str_log)
                    file1.close()
                    
                    # Check on forcing
                    input_dir=work_dir_HD+"/forcing/"
                    output_file=work_dir+"/forcing.nc"
                    
                    local_folder=work_dir+"/forcing"
                    
                    # BChoat: redefine size to compare size of output_file
                    size=0
                    if os.path.exists(output_file) :
                        size=os.path.getsize(output_file)
                        print ("File exist " + output_file)
                    
                    # troubleshooting
                    print(f'\n\nline 448\noutput_file: {output_file}\ninput_dir: {input_dir}\nlocal_folder: {local_folder}')
                    # Convert forcing from CSV to NETCDF if it does not exist    
                    # if NETCDF file size is < 5000, then assumed incorrect, so recreate.
                    if (not os.path.exists(output_file)) | (size<5000):
                        # troubleshooting
                        print(f'output_file is not a file --- in loop at line 374')

                        os.chdir(NextGen_folder+"/utilities/data_conversion")
                        str_sub="python csv2catchmentnetcdf.py -i "+input_dir+ " -o "+ output_file+ " -j 2"
                        out=subprocess.call(str_sub,shell=True)          
                        
                        str_sub="mv "+local_folder+ " "+ work_dir_HD
                        out=subprocess.call(str_sub,shell=True)          
                
                        str_sub="rm -rf "+work_dir
                        out=subprocess.call(str_sub,shell=True)   

                        # Go to working directory ... below here actions occur in work_dir -BChoat
                        os.chdir(work_dir)
                     
                    print(f'\n\nFolder_CAMELS: {Folder_CAMELS}')
                    # BChoat: hru_id is defined above. Not sure why being redefined here?
                    # hru_id=Selected_calibration.index[i]
                    
                    # BChoat troubleshooting
                    print(f'\n\nNow working in {work_dir}\n\n')
                    # Editing CFE configuration file  
                    str_sub="sed -i 's/gw_storage=0.05/gw_storage=0.35/g' "+work_dir+"/CFE/*"
                    out=subprocess.call(str_sub,shell=True)
                    str_sub="sed -i 's/soil_storage=0.05/soil_storage=0.35/g' "+work_dir+"/CFE/*"
                    out=subprocess.call(str_sub,shell=True)
                    
                    # troubleshooting
#                    print('\n\nRemoving flowveldepth... ngen_calibration... etc...\nline 401')
#                    print(f'\n~line 514: cwd = {os.getcwd()}\n')
                    print('\n\n Removing output files from previous run if they exist \n\n')
                    str_sub="rm flowveldepth_Ngen.h5"
                    out=subprocess.call(str_sub,shell=True)
                    # str_sub="rm test_log*"
                    # out=subprocess.call(str_sub,shell=True)
#                     str_sub="rm ngen-calibration* "
                    str_sub = 'rm objective_log.txt'
                    out=subprocess.call(str_sub,shell=True)
                    str_sub="rm reference.gpkg "
                    out=subprocess.call(str_sub,shell=True)   
                    str_sub="rm *parameter_df_state.parquet "
                    out=subprocess.call(str_sub,shell=True) 
                    
                    # troubleshooting
                    print(f'\n\nForcing = {Forcing}\n\n')
                    if(Forcing=="CSV"): 
                        # BChoat
                        print(f'\n\ncopying csvs back from expansion\n\n')
                        # since move all csvs to Expansion, copy back forcing.csv's if needed
                        str_sub="cp -r "+work_dir_HD+"/forcing ."
                        out=subprocess.call(str_sub,shell=True) 
                   
                    # BChoat: I don't think ngen-cal is in this directory
#                     print(f'\n~line 517: cwd = {os.getcwd()}')
#                     str_sub="rm -rf ./ngen-cal"
#                     out=subprocess.call(str_sub,shell=True)      
                    #str_sub="ln -s /home/west/git_repositories/ngen-cal"
                    # str_sub="ln -s /home/west/git_repositories/ngen-cal/"
                    #out=subprocess.call(str_sub,shell=True)  
                   
                    # remove ngen linked fold if it already exists, so can ensure correct
                    # NGEN being used
                    str_sub="rm -rf ./ngen"
                    out=subprocess.call(str_sub,shell=True)         
                    str_sub="ln -s "+NextGen_folder
                    out=subprocess.call(str_sub,shell=True)  
                    print(f'NextGen_folder = {NextGen_folder}')
                    # BChoat - getting error here: /bin/sh: 1: source: not found, so trying something different
#                    str_sub="source "+NextGen_folder+"/venv/bin/activate"
#                     str_sub = f"source {activate_use}"
#                    out=subprocess.call(str_sub,shell=True)  
                    # ensure subprocess inherits from current env
#                     out = subprocess.call(str_sub, shell = True, env = os.environ, executable = '/bin/bash')
#                     print('\nJust ran subprocess for activating venv env\n')
                    
                
                    # str_sub="aws s3 cp --recursive s3://formulations-dev/CAMELS20/"+Folder_CAMELS+"/parameters ./parameters/"  
                    # out=subprocess.call(str_sub,shell=True)  

                    str_sub="rm -rf ./t-route "
                    out=subprocess.call(str_sub,shell=True) 
                    
                    str_sub="cp -rf /home/west/Projects/CAMELS/CAMELS_Files_Ngen/t-route ."  
                    out=subprocess.call(str_sub,shell=True)  
                    
                    str_sub="cp "+calib_realiz_base + " ." 
                    out=subprocess.call(str_sub,shell=True)  
                    realiz_name=os.path.basename(calib_realiz_base)
                    calib_realiz=work_dir+realiz_name
                    
                    str_sub="cp "+calib_config_base + " ." 
                    out=subprocess.call(str_sub,shell=True)   
                    print(f'\njust ran {str_sub}\n')
                    
                    calib_name=os.path.basename(calib_config_base)
                    calib_config=work_dir+calib_name
                    # Modify calib_config to have correct parameters and directory
                    
                    with open(calib_config, 'r') as stream:
                        data_loaded_ori = yaml.load(stream,Loader=yaml.FullLoader)
                    data_loaded = data_loaded_ori.copy()
                    data_loaded['general']['workdir']=work_dir
                    data_loaded['general']['iterations']=iterations
                    data_loaded['model']['eval_params']['evaluation_start']=start_time
                    data_loaded['model']['eval_params']['evaluation_stop']=end_time
                    data_loaded['model']['eval_params']['objective']=flag_obj
                    data_loaded['model']['realization']="./"+realiz_name

                    print('\nline 552- just updated calib config yaml file\n')
                    
                    if(parallel_flag==1): 
                        data_loaded['model']['partitions']=hru_id+".json"
                        data_loaded['model']['parallel']=partition
                        data_loaded['model']['binary']="./ngen/cmake_build_paral/ngen"
                        str_sub=NextGen_folder+"/cmake_build_paral/partitionGenerator "+"./spatial/catchment_data.geojson ./spatial/nexus_data.geojson "+hru_id+".json "+str(partition) + " '' ''"
                        out=subprocess.call(str_sub,shell=True) 
                               
                    #catchment_data_file = work_dir/'spatial/catchment_data.geojson'
                    NWM_param_file=work_dir+'/parameters/cfe.csv'
                    soil_params=pd.read_csv(NWM_param_file,index_col=0)
                    soil_params['gw_Zmax'] = soil_params['gw_Zmax'].fillna(16.0)/1000.
                    soil_params['gw_Coeff'] = soil_params['gw_Coeff'].fillna(0.5)*3600*pow(10,-6)           
                    dict_param_name={"maxsmc":"sp_smcmax_soil_layers_stag=1",
                                     "satdk":"sp_dksat_soil_layers_stag=1",
                                     "slope":"sp_slope",
                                     "b":"sp_bexp_soil_layers_stag=1",
                                     "Cgw":"gw_Coeff",
                                     "expon":"gw_Expon",
                                     "satpsi":"sp_psisat_soil_layers_stag=1",
                                     "b":"gw_Expon",
                                     "max_gw_storage":"gw_Zmax",
                                     "refkdt":"sp_refkdt",
                                     "slope":"sp_slope",
                                     "wltsmc":"sp_smcwlt_soil_layers_stag=1",
                                     "x_Xinanjiang_shape_parameter":"x_Xinanjiang_shape_parameter"}
    
                    data_loaded_real_ori=json.load(open(calib_realiz))  
                    data_loaded_real=data_loaded_real_ori.copy()
                    calib_realiz_ini=calib_realiz.replace(".json","ini.json")
                    str_sub="cp "+calib_realiz+" " + calib_realiz_ini                      
                    out=subprocess.call(str_sub,shell=True)
                    print(f'\nline 585 - just ran {str_sub}\n')


                    # replace CFE variable if needed
                    if(Rainfall_Runoff_Model=="CFE") | (Rainfall_Runoff_Model=="CFE_X"): 
                        Xinanjiang_param="/home/west/Projects/CAMELS/params_code/Xinanj_params.csv"
                        Xin_param=pd.read_csv(Xinanjiang_param,index_col=0)
                        soil_params['x_Xinanjiang_shape_parameter']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['XXAJ'].values
                        print('\nline 593 - Just updated soil_params\n')
                        n_params=data_loaded['model']['params']['CFE']
                        for jj in range(0,len(data_loaded['cfe_params'])):
                            para=data_loaded['model']['params']['CFE'][jj]['name']
                            
                            if para in dict_param_name:
                                # BChoat - SHould this [j] be [jj]???
                                data_loaded['cfe_params'][j]['init']=str(soil_params[dict_param_name[para]].mean())
                            print(f'\nline601 - jj = {jj}\n')
#                        for jj in range(0,len(data_loaded['cfe_params'])):
                            para=data_loaded['model']['params']['CFE'][jj]['name']
                            print(f'\nline 604ish - para = {para}\n')
                            if para in dict_param_name:            
                                if('PET' in PET) & (Selected_calibration['frac_snow'].iloc[i]>=0.1):
#                                    print('\nline 607ish - in if(PET in PET) & (Selected_calibration...)\n')
                                    data_loaded_real['global']['formulations'][0]['params']['modules'][2]['params']['model_params'][para]=soil_params[dict_param_name[para]].mean() 
                                else:
                                    print('\nline 610ish - in else\n')
#                                    print(f'\ndata_loaded_real = {data_loaded_real}\n')
#                                    print(f'\nsoil_params[dict_param_name[para]].mean() = {soil_params[dict_param_name[para]].mean()}\n')
#                                    print(f"\ndata_loaded_real['global']['formulations'][0]['params']['modules'][2]['params'].keys() = \
#                                            {data_loaded_real['global']['formulations'][0]['params']['modules'][2]['params'].keys()}\n")
                                    # data_loaded_real['global']['formulations'][0]['params']['modules'][1]['params']['model_params'][para]=soil_params[dict_param_name[para]].mean() 
                                    data_loaded_real['global']['formulations'][0]['params']['modules'][2]['params']['model_params'][para]=soil_params[dict_param_name[para]].mean() 

#                            print(f'\nline609 - jj = {jj}\n')
       
                    if(Forcing=="CSV"): 
                        data_loaded_real['global']['forcing']={"file_pattern": "{{id}}.csv", "path": "./forcing/", "provider": "CsvPerFeature"}                 
                        
                    if(Forcing=="NetCDF"): 
                        data_loaded_real['global']['forcing']={'path': './forcing.nc', 'provider': 'NetCDF'} 
                        
                    print('\nline 614 - just updated config files\n')
                    json_object=json.dumps(data_loaded_real,indent=4)
                    with open(calib_realiz,"w") as outfile:
                        outfile.write(json_object) 
                        
                    with io.open(calib_config, 'w') as outfile:
                        yaml.dump(data_loaded, outfile)
                    
                
                    ########################################
                    # if more than gauge in catchment, keep only the one downstream - BChoat
                    str_sub="cp "+work_dir+"/parameters/cross-walk.json" + " " + work_dir+"/parameters/cross-walk_backup.json" 
                    out=subprocess.call(str_sub,shell=True)
                    print(f'\nline 627 - just ran {str_sub}\n')

                    
                    cross_walk_file=  work_dir+"/parameters/cross-walk.json"  
                    data_loaded_work_flow_ori=json.load(open(cross_walk_file))     
                    wb_ar=list(data_loaded_work_flow_ori.keys())
                    find_gage=0
                    
                    for ii in range(0,len(wb_ar)):
                        wb=wb_ar[ii]
                        remove_gage=0
                        if('Gage_no' in data_loaded_work_flow_ori[wb]):
                            if(data_loaded_work_flow_ori[wb]['Gage_no'][0]==hru_id):
                                print (" found the right gage ")
                                if(find_gage==1):
                                    print (" need to remove since it is duplicate")
                                    remove_gage=1
                                find_gage=1
                            else:
                                print (" need to remove since is not the gage to calibrate")
                                remove_gage=1
                        
                        if(remove_gage==1):
                            data_loaded_work_flow_ori[wb].pop('Gage_no', None)
                    
                    
                    json_object=json.dumps(data_loaded_work_flow_ori,indent=4)
                    with open(cross_walk_file,"w") as outfile:
                        outfile.write(json_object)                           
                    ######################################
                    
                    
                    #str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson \"all\" spatial/nexus_data.geojson \"all\" " + calib_realiz
                    #out=subprocess.call(str_sub,shell=True)  
                    # Ori_paramResults_old=calib_folder+"Ori_param/"           
                    # Ori_paramResults=work_dir+"/Ori_param/"
                    # os.mkdir(Ori_paramResults)
                    # str_sub="mv "+Ori_paramResults_old+"/* " +Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)
                    # str_sub="rm -rf "+Ori_paramResults_old
                    # out=subprocess.call(str_sub,shell=True)
                    # str_sub="mv cat*.csv "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)
                    # str_sub="mv nex*.csv "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)
                    # str_sub="mv tnx*.csv "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)    
                    # str_sub="mv flowveldepth_Ngen.h5* "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)            
        
                    #str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson \"all\" spatial/nexus_data.geojson \"all\" " + calib_realiz_ini
                    #out=subprocess.call(str_sub,shell=True)  
                    # Ori_paramResults_old=calib_folder+"Spatially_unif_ini/"
                    # Ori_paramResults=work_dir+"/Spatially_unif_ini/"
                    # os.mkdir(Ori_paramResults)
                    # str_sub="mv "+Ori_paramResults_old+"/* " +Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)
                    # str_sub="rm -rf "+Ori_paramResults_old
                    # out=subprocess.call(str_sub,shell=True)
        
                    
                    # os.mkdir(Ori_paramResults)
                    # str_sub="mv cat*.csv "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)
                    # str_sub="mv nex*.csv "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)
                    # str_sub="mv tnx*.csv "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)    
                    # str_sub="mv flowveldepth_Ngen.h5* "+Ori_paramResults
                    # out=subprocess.call(str_sub,shell=True)
          
                    # Test Run
                    # perform one run to test if operating correctly - BChoat
                    # Test_run="./ngen/cmake_build/ngen "+ work_dir+"spatial/catchment_data.geojson \"all\" "+work_dir+"spatial/nexus_data.geojson \"all\" "+calib_realiz

                    # BChoat commenting this out for now
#                     Test_run="./ngen/cmake_build/ngen spatial/catchment_data.geojson \"all\" spatial/nexus_data.geojson \"all\" "+calib_realiz

#                     print(f'\nTest_run = {Test_run}')

                    print(f'\nHydrofabrics_folder = {Hydrofabrics_folder}')
    
#                     f = open(Hydrofabrics_folder+"TestRuns.txt", "a")
                    
#                    out=subprocess.call(Test_run,shell=True,stdout=f)

 #                    print('\nJust ran job using subprocess call on Test_run, shown above\n')
                    #####################################

                    out=0
                    # BChoat - is it possible that out != 0, it is defined as 0 just above.
                    if(out==0):
                                                
                        print(f'\n\ncalib_name: {calib_name}\n\n')
#                         str_sub="python ./ngen-cal/python/calibration.py ./" +calib_name
#                         str_sub=f"{python_use} ./ngen-cal/python/calibration.py ./{calib_name}"
                        str_sub = f'{python_use} -m ngen.cal ./{calib_name}'
#                         str_sub = f'python -m ngen.cal ./{calib_name}'

                        # sudo /home/bchoat/Python/envs/NWMenv39/bin/python -m ngen.cal ./calib_config_CAMELS_Topmodel_Calib_Sep_2.yaml
                        # Running calibration 
                        print('Running calibration Ncat: ' + str(Selected_calibration.iloc[i]['NCat']))
                        start_run_time=time.time()
                        # troubleshooting - BChoat
#                        print(f'Current Working Directory: {os.getcwd()}')

                                              
                        # define path to ngen-cal library
                        # ngen_path = './ngen-cal/python/ngen_cal/src'
#                        if not ngen_path in sys.path:
#                            # sys.path.append('./ngen-cal/python/ngen_cal/src')
#                            sys.path.append(ngen_path)
#                         sys.path.insert(0, '/home/west/git_repositories/ngen-cal/python/ngen_cal/src')

#                         for path in sys.path:
#                             print(path)
                        
                        # troubleshooting
                        print(f'\nrunning {str_sub} - line 682')

                        which_py = subprocess.check_output('which python', shell = True)
                        which_py = which_py.decode('utf_8').strip()

                        print(f'\n\nWhich Python: {which_py}\n\n')


                        try:
                            out=subprocess.call(str_sub, shell=True)
                        except:
                            raise Exception("\n\n----\nERROR: calibration.py failed\n----\n\n")

                        # troubleshooting - BChoat
                        print(f'\n\nJust ran {str_sub}\n\n')
                        end_run_time=time.time()
                        elapsed_time = end_run_time - start_run_time
                        print('Execution time:', elapsed_time, 'seconds' + " Ncat: " + str(Selected_calibration.iloc[i]['NCat']))

                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        str_log="Finish running calibration,"+hru_id+","+dt_string+","+PET+","+Rainfall_Runoff_Model+"\n"
                        print(f'~line 858: str_log={str_log}')
                        file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
                        file1.write(str_log)
                        file1.close()
                        #str_sub="rm -rf calib1"
                        #out=subprocess.call(str_sub,shell=True)
                        
                        # flag=0;j=1
                        # while(flag==0):
                        #     calib_folder=work_dir+"calibSep_2_"+str(j)
                        #     if not os.path.exists(calib_folder): 
                        #         os.mkdir(calib_folder)
                        #         flag=1
                        #     j=j+1


                        # BChoat: Not sure why objective_log is being redfined here
                        # objective_log = work_dir+'ngen-calibration_objective.txt'    
                        # objective_log = f'{work_dir}ngen-calibration_objective.txt'
                        # int(f'\nobjective_log at line 804 - {objective_log}\n')
                        print(f'\n~line 839: cwd = {os.getcwd()}')
                        print(f'\nout = {out}\n')

                        # BChoat: later, the objective file is moved to the correct folder (e.g., cwd/NOAH_Topmodel)
                        # but here, it is just in the working directory, so ...
                        # Define a temporary location/filename for the objective file to check that it was created
                        temp_objfile = f'{os.getcwd()}/objective_log.txt'
                        if(os.path.exists(temp_objfile)):        
                            size=os.path.getsize(temp_objfile)
                            print(f'~line 881 - in if(os.path.exists(temp_objfile)')
                        else:
                            size=0
                        if(size==0) | (out>0):
                            # occasionally runs would error out in routing, so print error message here - BChoat
                            print ("Error in Calibration - did not copy files")
                            now = datetime.now()
                            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                            str_log="Return Error,"+hru_id+","+dt_string+","+PET+","+Rainfall_Runoff_Model+","+dt_string+",size="+str(size)+",out="+str(out)+"\n"
                            file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
                            file1.write(str_log) 
                            file1.close()
                            sys.exit()
#                            print('~ line 851; just before os.exit()')
#                            try:
#                                os.exit()
#                            except:
#                                print('os.exit() failed; try sys.exit()??')

                        else:
                            
                            print(f'~line903: in else: calib_folder_HD = {calib_folder_HD}')
                            # rmove calib_folder if it exists, because job will error out
                            # if it exists and is populated with older files
                            if os.path.exists(calib_folder_HD): 
                                str_sub = f'rm -r {calib_folder_HD}'
                                out = subprocess.call(str_sub, shell = True)
                            os.makedirs(calib_folder_HD, exist_ok=True)            
                            print('~line 906')
                            LastRun=calib_folder_HD+"LastRun/"
                            os.mkdir(LastRun)
                            # BestRun=calib_folder+"/Best_Results/"
                            # os.mkdir(BestRun)
                            print('~line 911') 
                            str_sub="mv ./Best_Results "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)
                            print('~line 914')
                            # files=glob.glob(BestRun+"/*")
                            # for i_file in files: shutil.move(i_file, i_file.replace(".best.","."))
                            
                            str_sub="mv cat*.csv "+LastRun
                            out=subprocess.call(str_sub,shell=True)
                            str_sub="mv nex*.csv "+LastRun
                            out=subprocess.call(str_sub,shell=True)
                            str_sub="mv tnx*.csv "+LastRun
                            out=subprocess.call(str_sub,shell=True)    
                            str_sub="mv flowveldepth_Ngen.h5* "+LastRun
                            out=subprocess.call(str_sub,shell=True)
                            
                            print('~line924')                            
                            str_sub="mv "+calib_config+" "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)
                            #str_sub="mv reference.gpkg "+calib_folder
                            #out=subprocess.call(str_sub,shell=True)          
                
                            # str_sub="mv ngen-calibration* "+calib_folder
                            str_sub = f'mv objective_log.txt {calib_folder_HD}'
                            out=subprocess.call(str_sub,shell=True)
                            # str_sub="mv reference.gpkg "+calib_folder
                            # out=subprocess.call(str_sub,shell=True)   
                            print(f'~line 935: calib_foler = {calib_folder_HD}')
                            str_sub="mv "+calib_realiz+" "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)
                            # str_sub="mv test_log* "+calib_folder
                            # out=subprocess.call(str_sub,shell=True)
                            #str_sub="cp reference.gpkg "+calib_folder
                            #out=subprocess.call(str_sub,shell=True) 
                            str_sub = f'mv best_params.txt {calib_folder_HD}'
                            out = subprocess.call(str_sub, shell = True)
                            str_sub="mv *parameter_df_state.parquet "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)                                                                                                                                                                                                                                                                                 
                            print('~line 945')
#                             str_sub = f'mv {calib_folder}/* {calib_folder_HD}'
#                             out=subprocess.call(str_sub,shell=True) 
                    else:  
                        NG_NotRunning=pd.concat([NG_NotRunning,Selected_calibration.iloc[i]])
                     
                except:
                     # troubleshooting -BChoat
                     print('\n\n-----------------In Exception-------------------\n\n')
                     now = datetime.now()
                     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                     str_log="Calibration Error,"+hru_id+","+dt_string+","+PET+","+Rainfall_Runoff_Model+",size="+str(size)+",out="+str(out)+"\n"
                     file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
                     file1.write(str_log)    
                     file1.close()

            else:
                continue
                  
                     
     
         
