#!/bin/bash

# bchoat 2023/07/19

# used to build ngen in Ubuntu 22.04

# Script builds and test ngen. Define a folder name which will be used for the home 
# directory for the build as well as for labeling a folder where the build and
# test logs will be saved.

# options should be edited around line 120, where cmake is used to build ngen.


# provide name for folder that will hold this ngen version
# NOTE: this folder is defined relative to the directory in which this file is located/executed.
folder_name="ngen_20231024"

################
# If want to build ngen-cal you need to include a line in the requirements.txt file
# Build ngen-cal?
# true of false?
# build_ngen-cal=true

# string defining requirements.txt file to use when building venv environment
# rqr_in should be defines relative to the directory in which this script is being execute.
# the script will copy it to $folder_name_ngen
rqr_in="requirements_20231024.txt"


# directory holding or where to place boost
boostDir=$PWD








#########################################################

# run deactivate and conda deactivate to ensure using clean slate for python environment
deactivate || true
conda deactivate || true

# define starting directory
baseDir=$PWD



#########
# update folder_name_ngen
mkdir "logs_${folder_name}"
folder_name_ngen="${folder_name}/ngen"
# define python location
# export Python_NumPy_INCLUDE_DIRS=/home/bchoat/Projects/NWM_NGEN/${folder_name_ngen}/.venv/lib/python3.10/site-packages
# export Python_NumPy_INCLUDE_DIR=/home/bchoat/Projects/NWM_NGEN/${folder_name_ngen}/.venv/lib/python3.10/site-packages


{
	echo "building in $folder_name_ngen"
	# install libraries
	echo -e "\n\ninstalling libraries into bash\n\n"
	sudo apt-get update &&
		sudo apt install cmake &&
		sudo apt-get install g++ &&
		sudo apt install gfortran &&
		sudo apt-get install python3-dev &&
		sudo apt install python3.10 &&
		sudo apt-get install libudunits2-dev &&
		sudo apt-get install libnetcdf-dev libnetcdff-dev &&
		sudo apt-get install libnetcdf-c++4-1 libnetcdf-c++4-dev ||
		exit 1
	
	 
	# clone ngen 
	echo -e "\n\ncloning ngen git repo\n\n"
	git clone https://github.com/noaa-owp/ngen $folder_name_ngen &&
		cd $folder_name_ngen &&
		# following line should update all submodules
		git submodule update --init --recursive ||
		exit 1
	# try updating t-route since get message that I'm using a deprecated version
# 	git submodule update --init --recursive --remote -- extern/t-route ||
# 		exit 1



	echo -e "\n\nbuilding ngen extern libraries\n\n"

	echo -e "\nBuild CFE\n"
	git submodule update --remote extern/cfe/cfe &&
	cmake -B extern/cfe/cmake_build -S extern/cfe/cfe -DBASE=OFF -DFORCING=OFF \
		-DFORCINGPET=OFF -DAETROOTZONE=OFF -DNGEN=ON &&
		make -C extern/cfe/cmake_build ||
		exit 1


	echo -e "\nBuild TOPMODEL\n"

	# replace topmodel repo with my own dev repo
	cd extern/topmodel/topmodel
	git remote add topmodelDev https://github.com/Ben-Choat/topmodel &&
		git fetch topmodelDev &&
		git checkout -b topmodelCal topmodelDev/remove-topmodel-output-fromNgen &&

	cd ../../../

	cmake -B extern/topmodel/cmake_build -S extern/topmodel &&
		make -C extern/topmodel/cmake_build ||
		exit 1

	echo -e "\nBuild PET\n"

	cmake -B extern/evapotranspiration/cmake_build -S \
			extern/evapotranspiration/evapotranspiration &&
		make -C extern/evapotranspiration/cmake_build petbmi -j2 &&
	
	echo -e "\nBuild SLoTH\n"
	cmake -B extern/sloth/cmake_build -S extern/sloth &&
		make -C extern/sloth/cmake_build ||
		exit 1
		
	
	# compile noah-owp and iso_c_fortran - add path to NetCDF libraries
	echo -e "\nbuild noah-owp and adding netcfd libraries\n"
	cmake -B extern/noah-owp-modular/cmake_build -S extern/noah-owp-modular \
		-DnetCDF_INCLUDE_DIR=/usr/include/ -DnetCDF_MOD_PATH=/usr/include/ \
		-DnetCDF_FORTRAN_LIB=/usr/lib/x86_64_linux_gnu/libnetcdff.so &&
		make -C extern/noah-owp-modular/cmake_build ||
		exit 1

	echo -e "build iso_c_fortran_bmi" 
	cmake -B extern/iso_c_fortran_bmi/cmake_build -S extern/iso_c_fortran_bmi &&
		make -C extern/iso_c_fortran_bmi/cmake_build ||
		exit 1


	echo -e "\nbuild test_bmi_c\n"
	cmake -B extern/test_bmi_c/cmake_build -S extern/test_bmi_c &&
		make -C extern/test_bmi_c/cmake_build ||
		exit 1
	
	echo -e "\nbuild test_bmi_fortran\n"
	cmake -B extern/test_bmi_fortran/cmake_build -S extern/test_bmi_fortran &&
		make -C extern/test_bmi_fortran/cmake_build ||
		exit 1

	# get boost library if not already stored in project folder
	echo -e "\n\ninstalling boost if needed\n\n"
	if [ ! -d "${boostDir}/boost_1_77_0" ]; then
		wget -O boost_1_77_0.tar.gz \
			https://boostorg.jfrog.io/artifactory/main/release/1.77.0/source/boost_1_77_0.tar.gz
		tar xzvf boost_1_77_0.tar.gz ||
		exit 1
	fi


	
	# create python virtual environment
	echo -e "\n\ninstalling python libraries w/venv\n\n"
	# install python-venv to get ensurepip
	sudo apt install python3.10-venv
	# copy requirments file to $folder_name_ngen
	sudo cp $baseDir/$rqr_in .
	mkdir venv &&
		python3 -m venv venv &&
		source venv/bin/activate &&
		pip install -r $rqr_in ||
		exit 1		 
	
	echo -e "\n\nprepending venv directory to PATH\n\n"
# 	echo -e "Set assuming PWD = ${PWD}\n\n"
	export PATH="${PWD}/venv/bin:$PATH"


	echo -e "\ncompile t-route\n"
	

	##################
        # t-route
        # download

        ################
        # Working with newest t-route
        ################

#       # first, remove default t-route folder that comes with ngen, it is old
#       cd extern
##      sudo rm -rf t-route
#       mv t-route t-route_ORG
#       # now clone the new t-route
#       git clone --progress --single-branch --branch master http://github.com/NOAA-OWP/t-route.git
#
#       cd t-route
#
#       # compile and install
#       ./compiler.sh

	###############
	# Working with default t-route (version that comes with ngen repo
	##############
	cd $baseDir/$folder_name_ngen/extern/t-route/src/python_routing_v02
	echo -e $PWD
	./compiler.sh


	# compile ngen -Add boost path -with routing
	cd $baseDir/$folder_name_ngen
	echo -e "\n\nbuilding ngen\n\n"
	cmake -DCMAKE_BUILD_TYPE=Debug -B cmake_build -S . \
		-DBoost_INCLUDE_DIR=$boostDir/boost_1_77_0 \
		-DNGEN_ACTIVATE_PYTHON:BOOL=ON \
		-DNGEN_ACTIVATE_ROUTING:BOOL=ON \
		-DBMI_C_LIB_ACTIVE:BOOL=ON \
		-DBMI_FORTRAN_ACTIVE:BOOL=ON \
		-DNETCDF_ACTIVE:BOOL=ON &&
		# -DMPI_ACTIVE:=BOOL=ON && \
		# -DLSTM_TORCH_LIB_ACTIVE:=ON && \
		make -j 8 -C cmake_build ||
		exit 1





	###################	

	# copy build_ngen.sh and requirements.txt files to build folder
#	cd $baseDir/$folder_name
#	echo -e "${baseDir}/${folder_name_ngen}"
	echo -e "PWD: $PWD\n"
	sudo mkdir "${baseDir}/${folder_name}/BuildScripts"
	sudo mv "${baseDir}/${folder_name_ngen}/${rqr_in}" "${baseDir}/${folder_name}/BuildScripts"
	sudo cp "${baseDir}/build_ngen.sh" "${baseDir}/${folder_name}/BuildScripts"

	cd $baseDir

} | tee -a "logs_${folder_name}/build_log.txt" 2>&1

{	
	echo -e "\n\ntesting ngen bmi installs\n\n"
#	cd $baseDir/$folder_name_ngen
	cd "${baseDir}/${folder_name_ngen}"
	echo -e "PWD: $PWD\n"

	source "${folder_name_ngen}/venv/bin/activate"


#	./cmake_build/test/test_all &&
	./cmake_build/test/test_bmi_c &&
	./cmake_build/test/test_bmi_fortran &&
	./cmake_build/test/test_bmi_python ||
	exit 1

	# t-route
#	echo -e "\n\ntesting t-route\n\n"
#	source venv/bin/activate
#	cd extern/t-route/test/LowerColorado_TX
#	python -m nwm_routing -f test_AnA.yaml


	# CODE FROM LUCIANA - OLD
	# t-route unit-test (changing syntax for consistency
#	echo -e "\n\nbuilding and testing test_routing_pybind\n\n"
	# make -C cmake_build test_routing_pybind &&
#	cmake --build cmake_build --target test_routing_pybind &&
# 	cmake -B cmake_build -S 
#	./cmake_build/test/test_routing_pybind ||
#		exit 1

} | tee -a "logs_${folder_name}/test_log.txt" 2>&1

# move logs to new build
mv "logs_${folder_name}" $folder_name

