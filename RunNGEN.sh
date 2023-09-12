#!/bin/bash

./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_szm_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_t0_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_td_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_chv_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_rv_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_srmax_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_sr0_calibNC.json

# MULTIPLE PARAMS
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_chv_td_calibNC.json


# GREEN-AMPT RELATED
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_xk0_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_hf_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_dth_calibNC.json


# TROUBLE SHOOTING
# valgrind --leak-check=yes --track-origins=yes ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_calibNC.json
# valgrind --leak-check=yes -s ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_calibNC.json > valgrind_log.txt 2>&1
# valgrind --leak-check=yes --track-origins=yes ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_chv_calibNC.json
# valgrind --leak-check=yes -s ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_pet_Topmodel_chv_calibNC.json






# JUST FOR STORING
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_Topmodel_calibNC.json
# ./ngen spatial/catchment_data.geojson cat-12 ./spatial/nexus_data.geojson cat-12 Realizations/Realization_Topmodel_Parm_calibNC.json




