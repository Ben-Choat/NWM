#!/bin/bash

# give name to include in log file
run_name="1_PET_Topmodel"

source $PWD/ngen/venv/bin/activate
which_python=$(which python)
echo $which_python

# get start time
start_time=$(date +%s)
echo "start_time: $start_time"


##############
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_cfe_calibNC.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_cfe_calibNC_tested.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_cfe_calibNC_DELETE.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_pet_cfe_calibNC.json

# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_pet_cfe_X_calibNC.json



# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_testNels.json

# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_cfe_calibNC_Modtested.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_pet_cfe_calibNC.json

##### Run in parallel
#create parallel partition

ngen/cmake_build/partitionGenerator spatial/catchment_data.geojson spatial/nexus_data.geojson partition_config.json 1 '' ''
mpirun -n 1 ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_Topmodel_calibNC.json partition_config.json
####

# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_Topmodel_calibNC.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_pet_Topmodel_calibNC.json

# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_pet_Topmodel_calibNC.json

# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_Topmodel.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_Topmodel_calibNC.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_Topmodel_calibNCTEST.json



# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_Topmodel_calibNC_NOtroute.json
# ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_cfe_calibNC_NOtroute.json
# valgrind --leak-check=yes ngen/cmake_build/ngen spatial/catchment_data.geojson "all" spatial/nexus_data.geojson "all" Realization_noahowp_cfe_calibNC.json > valgrind_output.txt 2>&1
#############


# get end time
end_time=$(date +%s)
echo "end_time: $end_time"
total_time=$(($end_time-$start_time))

echo "Run: $run_name" >> "runs.log"
echo "start time: $start_time" >> "runs.log"
echo "end time: $end_time" >> "runs.log"
printf "run time: $total_time\n\n" >> "runs.log"
