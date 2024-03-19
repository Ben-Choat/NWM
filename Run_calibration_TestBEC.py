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

NextGen_folder = "/home/west/git_repositories/ngen_20240111_calib/ngen"
print(f'\n\nUsing NGEN install located in: {NextGen_folder}\n')

# Define which python to use when calling subprocess.call(python ...) - BChoat
python_use = f"{NextGen_folder}/venv/bin/python"

# Forcing variable is used to update Realization templates and to 
# move files as needed
Forcing="NetCDF" # NEed to adapt realization and ngen-cal code

# set number of iterations for using TOPMODEL and CFE/CFE_X
# NOTE: ngen-cal requires number of iterations to be >= 2
tm_iterations = 2 # 120 # 2 # 120
cfe_iterations = 2 # 300 #2 # 300

# set the minimum number of nexuses that must be present for a job to run
# BChoat, 2024/1/10
# in earlier versions, hdf5 file was not produced if < 2 nexuses were present.
# so for first round of calibrations there was required to be >= 2 nexuses.
# We may test if this has been fixed later. If so, we can add basins.
min_nexuses = 2

# manually running in parallel by running serial jobs in different temrinals
# so define min and max number catchments
# dividing by 0, 12, 18, 32, 48, and 1000
min_ncat = 0 
max_ncat = 100000

# if want to run test runs, provide hru_ids for catchments here
# set as empty list if do not want to run tests
# hru_run = ['10259000', '08066300']
hru_run = []

# main folder holding individual HRU information (i.e., the main working directories for this script
Hydrofabrics_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
Hydrofabrics_folder_HD="/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen_Test/"

# file holding information about best models and runs. 
# Used as basis for subsetting to hru's we are working with here.
# Select_calibration_file="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/Select_calibration_HLR_RFC.csv"
# Selected_calibration = Selected_calibration[~Selected_calibration.index.duplicated(keep='first')]
# Select_calibration_file="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/SelectModelCal/CAMELS_v3_calib_BestModels.csv"
# Select_calibration_file="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_calib_BestModelsAll.csv"
# Select_calibration_file="/home/west/Projects/CAMELS/NextGenCode/Calibration/TM_CalibTestCatchments.csv"
# Select_calibration_file="/home/west/Projects/CAMELS/NextGenCode/Calibration/ParallelTestCatchments.csv"
Select_calibration_file="/home/west/Projects/CAMELS/NextGenCode/Calibration/ParallelTestCatchment_13235000.csv"



# working with Selected_calibration_file
# do not need this since same info in AllBasins2023-03-141248.csv read in below
ALL=pd.read_csv(Select_calibration_file,dtype={'hru_id_CAMELS': str})
ALL=ALL.set_index(['hru_id_CAMELS'])
ALL=ALL.rename(columns={'N_Nexus':'N_nexus'})
# get columns to drop
colDrop = [x for x in ALL.columns if "Q_Best_" in x]
# ALL=ALL.drop(['Q_Best_Topmodel','Q_Best_CFE_X'],axis=1).dropna()
# print(f"ALL (Select_Calibration): {ALL}")
# ALL=ALL.drop(colDrop, axis = 1).dropna()
# print(f"ALL (Select_Calibration): {ALL}")



Selected_calibration=ALL.copy()
# set up environment to enable everything to be ran using correct venv env and bash
os.environ['PATH']=NextGen_folder+"/venv/bin:/usr/bin:"

# define directory holding template configuration files
# (e.g., Realization... and calib_config files)
calib_config_dir="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/calib_conf/"

# these are evaluation times - not run times
start_time="2008-10-01 00:00:00"
# end_time="2013-10-01 00:00:00"
end_time="2008-10-05 00:00:00"


# Rainfall_Runoff_ModelAr=["CFE","CFE_X","Topmodel"]
# Rainfall_Runoff_ModelAr=['Topmodel']
Rainfall_Runoff_ModelAr=["CFE"]
NG_NotRunning=pd.DataFrame()

# create lists/variables for tracking progress
run=0
idd=[]

# File with subset of catchments that have been prioritized
# prioritized small basins w/ > 2 nexuses
# Priority_file='/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Calib_plots_Primary/AllBasins2022-11-291248.csv'
# Priority_file='/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Calib_plots_Primary_Original/AllBasins2022-12-061248.csv'
Priority_file='/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Calib_plots_Primary/AllBasins2022-11-291248.csv'


# Priority_file = '/home/west/Projects/CAMELS/CAMELS_Files_Ngen/ForPaper/AllBasins2023-03-141248.csv'
Priority=pd.read_csv(Priority_file,dtype={'hru_id_CAMELS': str})

print(f"Selected_calibration.index; {Selected_calibration.index}")
# subset to hru's in Selected_calibrations
Priority = Priority[Priority['hru_id_CAMELS'].isin(Selected_calibration.index)]
Priority=Priority.set_index(['hru_id_CAMELS'])
Priority=Priority.dropna()

print(f'Priority: {Priority}')

# subset to HRU's as desired
# BChoat - Editing to run any catchment that previously had output for CFE or CFE_X
# this is because we want to run the same catchments for topmodel, that have
# previously been ran for CFE and/or CFE_X
# Priority=Priority[(Priority['CFE']==1) | (Priority['CFE_X']==1)]
#Priority=Priority[(Priority['CFE']==1) | (Priority['CFE_X']==1) | (Priority['Topmodel']==1)]
#Priority['Sum']=Priority['CFE']+Priority['CFE_X']+Priority['Topmodel']
#Priority=Priority[Priority['Sum']==1]
#Priority=Priority[(Priority['Sum']>=2)]

print(f'Selected_calibration: {Selected_calibration}')
print(f'Priority.index.values: {Priority.index.values}')
# BChoat: we only want to run HRUs that were previously ran for CFE, so subset to those catchments
Selected_calibration=Selected_calibration.loc[Priority.index.values]
Selected_calibration=Selected_calibration.sort_values(by="NCat")
print(f'Selected_calibration: {Selected_calibration}')

try:
    Selected_calibration=Selected_calibration.drop('04197170')
except:
    pass


######################
# Chunk for running specific basins based on hru_id
# extract to test basins

try:
    if len(hru_run) > 0:
        # subset to hru_run list defined above
        Selected_calibration = Selected_calibration.loc[hru_run]
except:
    pass
######################

# subset to HRUs where min_ncat<=NCat<max_ncat
Selected_calibration = Selected_calibration[
        (Selected_calibration['NCat'] >= min_ncat) &\
        (Selected_calibration['NCat'] < max_ncat)
        ]

# print current python as sanity check
which_py = subprocess.check_output('which python', shell = True)
which_py = which_py.decode('utf_8').strip()

print(f'\n\nWhich Python: {which_py}\n\n')


flag_obj="kling_gupta"

if flag_obj == 'kling_gupta':
    str_obj = ''
elif flag_obj == 'nnse':
    str_obj = 'nnse'
else:
    print('No objective, or invalid objective, defined')


for i in range(0,len(Selected_calibration)):
# for i in range(0, 1):
# for i in range(0, 3):
    Folder_CAMELS=Selected_calibration.iloc[i]['Folder_CAMELS']
    hru_id=Selected_calibration.index[i]

    print(f'Number of catchments = {Selected_calibration.iloc[i]["NCat"]}')
    # set up partition file for running in parallel - BChoat
    if Selected_calibration.iloc[i]['NCat'] < 12: partition = 1 # 1
    elif Selected_calibration.iloc[i]["NCat"] < 18: partition = 1 # 1 #2
    elif Selected_calibration.iloc[i]["NCat"] < 1: partition = 1 # 1 # 4 
    elif Selected_calibration.iloc[i]["NCat"] < 48: partition = 1 # 1 # 8
    elif Selected_calibration.iloc[i]["NCat"] < 64: partition = 1 # 1 # 8
    elif Selected_calibration.iloc[i]["NCat"] < 90: partition = 1 # 1 # 8

 
    else:  partition = 1 # 1 # 16
        
        
    for j in range(0, len(Rainfall_Runoff_ModelAr)):
        # runs failed when N_nexus == 1, so skip if that is the case - BChoat
        # Later test to see if fixed, and can include some N_nexus == 1 catchments
        if(Selected_calibration.iloc[i]['N_nexus']<2):
        #if(Selected_calibration.iloc[i]['frac_snow']>0.1) & ('PET' in Selected_calibration.iloc[i]['A_Best1']):
            print("Not running, N_nexus < 2 "+Folder_CAMELS)
        else:
         
            run=run+1
            idd.append(i)
           
            #PET=Best_PET.loc[hru_id]
            PET=Selected_calibration.iloc[i]['A_Best1']
            
            Rainfall_Runoff_Model=Rainfall_Runoff_ModelAr[j]
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            str_log="\nCollecting params for,"+hru_id+","+dt_string+","+PET+","+Rainfall_Runoff_Model+"\n"
            file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
            file1.write(str_log)    
            file1.close()
            
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
            
            # define folder on external hard drive in which results and calibration info will be stored
            calib_folder_HD=Hydrofabrics_folder_HD+"Results/"+Folder_CAMELS+"/Calibration/"+Model+"/" +Model+str_obj+"/"
            print(f'\n\ncalib_folder_HD: {calib_folder_HD}\n\n')
            
            # define objective log location/name on exertnal hard drive to see if it existsj
            # and to store when done
            objective_log_HD = f'{calib_folder_HD}objective_log.txt'
            print(f'\nobjective_log_HD: {objective_log_HD}\n\n')                  


            # Check if the objective file already exists in
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

            
                        
            # run calibration if N_nexus>= min_nexuses (defined above)
            if(Selected_calibration.iloc[i]['N_nexus']>=min_nexuses): # & (size<100):
                print(f'\nRunning {Folder_CAMELS}\n\n')
                             
                try:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    str_log="\n\nStarted running calibration,"+hru_id+","+dt_string+"\n"
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
                    
                    # Convert forcing from CSV to NETCDF if it does not exist    
                    # if NETCDF file size is < 5000, then assumed incorrect, so recreate.
                    if (not os.path.exists(output_file)) | (size<5000):

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
                                                
                    # Editing CFE configuration file  
                    str_sub="sed -i 's/gw_storage=0.05/gw_storage=0.35/g' "+work_dir+"/CFE/*"
                    out=subprocess.call(str_sub,shell=True)
                    str_sub="sed -i 's/soil_storage=0.05/soil_storage=0.35/g' "+work_dir+"/CFE/*"
                    out=subprocess.call(str_sub,shell=True)
                    
                    print('\n\n Removing output files from previous run if they exist \n\n')
                    str_sub="rm flowveldepth_Ngen.h5"
                    out=subprocess.call(str_sub,shell=True)
                    str_sub = 'rm objective_log.txt'
                    out=subprocess.call(str_sub,shell=True)
                    str_sub="rm reference.gpkg "
                    out=subprocess.call(str_sub,shell=True)   
                    str_sub="rm *parameter_df_state.parquet "
                    out=subprocess.call(str_sub,shell=True) 
                    
                    # print update about forcing
                    print(f'\n\nForcing = {Forcing}\n\n')
                    if(Forcing=="CSV"): 
                        # BChoat
                        print(f'\n\ncopying csvs back from expansion\n\n')
                        # since move all csvs to Expansion, copy back forcing.csv's if needed
                        str_sub="cp -r "+work_dir_HD+"/forcing ."
                        out=subprocess.call(str_sub,shell=True) 
                   
                    # remove ngen linked folder if it already exists, so can ensure correct
                    # NGEN being used
                    str_sub="rm -rf ./ngen"
                    out=subprocess.call(str_sub,shell=True)         
                    str_sub="ln -s "+NextGen_folder
                    out=subprocess.call(str_sub,shell=True)  
                    print(f'NextGen_folder = {NextGen_folder}')

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

                    
                    # if(parallel_flag==1): 
                    data_loaded['model']['partitions'] = f'{hru_id}.json'
                    data_loaded['model']['parallel']=partition

                    # generate the partition.json file (names as hru_id.json)
                    str_sub = f"{NextGen_folder}/cmake_build/partitionGenerator ./spatial/catchment_data.geojson ./spatial/nexus_data.geojson {hru_id}.json {partition} '' ''"
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


                    # replace CFE variable if needed
                    if(Rainfall_Runoff_Model=="CFE") | (Rainfall_Runoff_Model=="CFE_X"): 
                        print("line 460; in RRM==CFE | RRM=CFE_X")
                        Xinanjiang_param="/home/west/Projects/CAMELS/params_code/Xinanj_params.csv"
                        Xin_param=pd.read_csv(Xinanjiang_param,index_col=0)
                        soil_params['x_Xinanjiang_shape_parameter']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['XXAJ'].values
                        n_params=data_loaded['model']['params']['CFE']
                        for jj in range(0,len(data_loaded['cfe_params'])):
                            para=data_loaded['model']['params']['CFE'][jj]['name']
                            
                            if para in dict_param_name:
                                data_loaded['cfe_params'][j]['init']=str(soil_params[dict_param_name[para]].mean())
                            para=data_loaded['model']['params']['CFE'][jj]['name']

                            if para in dict_param_name:            
                                print("line 473; in para in dict...")
                                if('PET' in PET) & (Selected_calibration['frac_snow'].iloc[i]>=0.1):
                                    print("line 475")
                                    print(f"para: {para}")

                                    print(f"soil_params[dict_param_name[para]].mean(): {soil_params[dict_param_name[para]].mean()}")
                                    print(f"data_loaded_real: {data_loaded_real}")

                                    print(f"calib_realiz: {calib_realiz}")

                                    print(f"data_loaded_real['global']['formulations'][0]['params']['modules'][2]:"\
                                            f"{data_loaded_real['global']['formulations'][0]['params']['modules'][2]}")

                            
                                    print(f"data_loaded_real['global']['formulations'][0]['params']['modules'][3]['params']['model_params']:"\
                                            f"{data_loaded_real['global']['formulations'][0]['params']['modules'][3]['params']['model_params']}")

#                                     print(f"data_loaded_real['global']['formulations'][0]['params']['modules'][2]['params']['model_params'][para]:"\
#                                             f"{data_loaded_real['global']['formulations'][0]['params']['modules'][2]['params']['model_params'][para]}")
                                    data_loaded_real['global']['formulations'][0]['params']['modules'][3]['params']['model_params'][para]=soil_params[dict_param_name[para]].mean() 
                                    print("line 477")
                                else:
                                    data_loaded_real['global']['formulations'][0]['params']['modules'][3]['params']['model_params'][para]=soil_params[dict_param_name[para]].mean() 
                                    

                        print("line478; still in xxx|xxxx")
     
                    if(Forcing=="CSV"): 
                        data_loaded_real['global']['forcing']={"file_pattern": "{{id}}.csv", "path": "./forcing/", "provider": "CsvPerFeature"}                 
                        
                    if(Forcing=="NetCDF"): 
                        data_loaded_real['global']['forcing']={'path': './forcing.nc', 'provider': 'NetCDF'} 
                    print("line 483; just passed Forcing==xxx")
                        
                    json_object=json.dumps(data_loaded_real,indent=4)
                    with open(calib_realiz,"w") as outfile:
                        outfile.write(json_object) 
                        
                    with io.open(calib_config, 'w') as outfile:
                        yaml.dump(data_loaded, outfile)
                    
                
                    ########################################
                    # if more than gauge in catchment, keep only the one downstream - BChoat
                    str_sub="cp "+work_dir+"/parameters/cross-walk.json" + " " + work_dir+"/parameters/cross-walk_backup.json" 
                    out=subprocess.call(str_sub,shell=True)
                    
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
                    
                    
          
                    # Test Run
                    # perform one run to test if operating correctly - BChoat
                    # Test_run="./ngen/cmake_build/ngen "+ work_dir+"spatial/catchment_data.geojson \"all\" "+work_dir+"spatial/nexus_data.geojson \"all\" "+calib_realiz

                    # BChoat commenting this out for now
#                     Test_run="./ngen/cmake_build/ngen spatial/catchment_data.geojson \"all\" spatial/nexus_data.geojson \"all\" "+calib_realiz

#                     print(f'\nTest_run = {Test_run}')

                    print(f'\nHydrofabrics_folder = {Hydrofabrics_folder}')
    

                    out=0
                    # BChoat - is it possible that out != 0, it is defined as 0 just above.
                    if(out==0):
                                                
                        print(f'\n\ncalib_name: {calib_name}\n\n')
                        print(f'realization file name: {calib_realiz}')
                        str_sub = f'{python_use} -m ngen.cal ./{calib_name}'

                        # Running calibration 
                        print('Running calibration Ncat: ' + str(Selected_calibration.iloc[i]['NCat']))
                        start_run_time=time.time()
                        
                        # troubleshooting
#                        which_py = subprocess.check_output('which python', shell = True)
#                        which_py = which_py.decode('utf_8').strip()
#                        print(f'\n\nWhich Python: {which_py}\n\n')


                        try:
                            out=subprocess.call(str_sub, shell=True)
                        except:
                            raise Exception("\n\n----\nERROR: calibration.py failed\n----\n\n")

                        end_run_time=time.time()
                        elapsed_time = end_run_time - start_run_time
                        print('\n\n---------------------------------------\n\n')
                        print('Execution time:', elapsed_time, 'seconds' + " Ncat: " + str(Selected_calibration.iloc[i]['NCat']))
                        print('\n\n---------------------------------------\n\n')


                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        str_log="Finish running calibration,"+hru_id+","+dt_string+","+PET+","+Rainfall_Runoff_Model+"\n"
                        str_part = f"N_Partitions: {partition}\n"
                        str_elapsed = f'Elapased Time: {elapsed_time} seconds\n\n'
                        file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
                        file1.write(str_log)
                        file1.write(str_part)
                        file1.write(str_elapsed)
                        file1.close()
                    
                        # BChoat: later, the objective file is moved to the correct folder (e.g., cwd/NOAH_Topmodel)
                        # but here, it is just in the working directory, so ...
                        # Define a temporary location/filename for the objective file to check that it was created
                        temp_objfile = f'{os.getcwd()}/objective_log.txt'
                        if(os.path.exists(temp_objfile)):        
                            size=os.path.getsize(temp_objfile)
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

                        else:
                            print(f'\n\nMoving output files and information to {calib_folder_HD}\n\n')
                            print('\n\n---------------------------------------')
                            print('---------------------------------------\n\n')


                            # remove calib_folder if it exists, because job will error out
                            # if it exists and is populated with older files
                            if os.path.exists(calib_folder_HD): 
                                str_sub = f'rm -r {calib_folder_HD}'
                                out = subprocess.call(str_sub, shell = True)
                            os.makedirs(calib_folder_HD, exist_ok=True)            
                            LastRun=calib_folder_HD+"LastRun/"
                            os.mkdir(LastRun)
                            str_sub="mv ./Best_Results "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)                            
                            str_sub="mv cat*.csv "+LastRun
                            out=subprocess.call(str_sub,shell=True)
                            str_sub="mv nex*.csv "+LastRun
                            out=subprocess.call(str_sub,shell=True)
                            str_sub="mv tnx*.csv "+LastRun
                            out=subprocess.call(str_sub,shell=True)    
                            str_sub="mv flowveldepth_Ngen.h5* "+LastRun
                            out=subprocess.call(str_sub,shell=True)
                            str_sub = f'mv *log* {calib_folder_HD}'
                            out = subprocess.call(str_sub, shell = True)
                            str_sub="mv "+calib_config+" "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)
                            str_sub = f'mv objective_log.txt {calib_folder_HD}'
                            out=subprocess.call(str_sub,shell=True)
                            str_sub="mv "+calib_realiz+" "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)
                            str_sub = f'mv best_params.txt {calib_folder_HD}'
                            out = subprocess.call(str_sub, shell = True)
                            str_sub="mv *parameter_df_state.parquet "+calib_folder_HD
                            out=subprocess.call(str_sub,shell=True)                                                                                                                                                                                                                                                                                  
                    else:  
                        NG_NotRunning=pd.concat([NG_NotRunning,Selected_calibration.iloc[i]])
                     
                except:
                     print('\n\n-----------------In Exception-------------------\n\n')
                     now = datetime.now()
                     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                     str_log="Calibration Error,"+hru_id+","+dt_string+","+PET+","+Rainfall_Runoff_Model+",size="+str(size)+",out="+str(out)+"\n"
                     file1 = open(Hydrofabrics_folder+"calib_log.txt", "a")  # append mode
                     file1.write(str_log)    
                     file1.close()

            else:
                continue
                  
                     
     
         
