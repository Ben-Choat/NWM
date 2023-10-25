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
# the script will copy it to $folder_name
rqr_in="requirements_20231024.txt"

mkdir logs_${folder_name}

# run deactivate and conda deactivate to ensure using clean slate for python environment
deactivate || true
conda deactivate || true

# define python location
# export Python_NumPy_INCLUDE_DIRS=/home/bchoat/Projects/NWM_NGEN/${folder_name}/.venv/lib/python3.10/site-packages
# export Python_NumPy_INCLUDE_DIR=/home/bchoat/Projects/NWM_NGEN/${folder_name}/.venv/lib/python3.10/site-packages


{
	echo "building in $folder_name"
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
	
	# get boost library if not already stored in project folder
	echo -e "\n\ninstalling boost if needed\n\n"
	if [ ! -d "boost_1_77_0" ]; then
		wget -O boost_1_77_0.tar.gz \
			https://boostorg.jfrog.io/artifactory/main/release/1.77.0/source/boost_1_77_0.tar.gz
		tar xzvf boost_1_77_0.tar.gz ||
		exit 1
	fi
	 
	# clone ngen 
	echo -e "\n\ncloning ngen git repo\n\n"
	git clone https://github.com/noaa-owp/ngen $folder_name &&
		cd $folder_name &&
		git submodule update --init --recursive ||
		exit 1
	# try updating t-route since get message that I'm using a deprecated version
	git submodule update --init --recursive --remote -- extern/t-route ||
		exit 1

        # replace topmodel repo with my own dev repo
	cd extern/topmodel/topmodel
	git remote add topmodelDev https://github.com/Ben-Choat/topmodel
	git fetch topmodelDev
	git checkout -b topmodelCal topmodelDev/remove-topmodel-output-fromNgen


	
	
	
	echo -e "\n\nbuilding ngen extern libraries\n\n"
	cmake -B extern/cfe/cmake_build -S extern/cfe/cfe -DBASE=OFF -DFORCING=OFF \
			-DFORCINGPET=OFF -DAETROOTZONE=OFF -DNGEN=ON &&
	
		make -C extern/cfe/cmake_build &&
		cmake -B extern/topmodel/cmake_build -S extern/topmodel &&
		make -C extern/topmodel/cmake_build &&
		cmake -B extern/evapotranspiration/cmake_build -S \
			extern/evapotranspiration/evapotranspiration &&
		make -C extern/evapotranspiration/cmake_build petbmi -j2 &&
		cmake -B extern/sloth/cmake_build -S extern/sloth &&
		make -C extern/sloth/cmake_build ||
		exit 1
		
	
	# compile noah-owp and iso_c_fortran - add path to NetCDF libraries
	echo -e "\n\nbuilding noah-owp and iso_c_fortran and adding netcfd libraries\n\n"
	cmake -B extern/noah-owp-modular/cmake_build -S extern/noah-owp-modular \
		-DnetCDF_INCLUDE_DIR=/usr/include/ -DnetCDF_MOD_PATH=/usr/include/ \
		-DnetCDF_FORTRAN_LIB=/usr/lib/x86_64_linux_gnu/libnetcdff.so &&
		make -C extern/noah-owp-modular/cmake_build &&
		cmake -B extern/iso_c_fortran_bmi/cmake_build -S extern/iso_c_fortran_bmi &&
		make -C extern/iso_c_fortran_bmi/cmake_build ||
		exit 1
	
	# create python virtual environment
	echo -e "\n\ninstalling python libraries w/venv\n\n"
	# install python-venv to get ensurepip
	sudo apt install python3.10-venv
	# copy requirments file to $folder_name
	sudo cp ../$rqr_in .
	mkdir venv &&
		python3 -m venv venv &&
		source venv/bin/activate &&
		pip install -r $rqr_in ||
		# pip install numpy &&
		# pip install -U pip setuptools cython dask &&
		# pip install deprecated &&
		# pip install bmipy &&
		# pip install tables && #   --hdf5=/usr/lib &&
		# pip install pydantic || # &&
#		pip install pybind11 ||
		exit 1		
	
	
      
	
	
	
	echo -e "\n\nprepending venv directory to PATH\n\n"
	echo -e "Set assuming PWD = ${PWD}\n\n"
	export PATH="${PWD}/venv/bin:$PATH"

	echo $PATH

	# compile ngen -Add boost path -with routing
	echo -e "\n\nbuilding ngen\n\n"
	cmake -DCMAKE_BUILD_TYPE=Debug -B cmake_build -S . \
		-DBoost_INCLUDE_DIR=/home/ubuntu/boost_1_77_0 \
		-DNGEN_ACTIVATE_PYTHON:BOOL=ON \
		-DNGEN_ACTIVATE_ROUTING:BOOL=ON \
		-DBMI_C_LIB_ACTIVE:BOOL=ON \
		-DBMI_FORTRAN_ACTIVE:BOOL=ON \
		-DNETCDF_ACTIVE:=ON &&
		# -DMPI_ACTIVE:=BOOL=ON && \
		# -DLSTM_TORCH_LIB_ACTIVE:=ON && \
		make -j 8 -C cmake_build &&

		echo -e "\n\nPWD: $PWD\n\n"
	
		# bmi_c
		cmake -B extern/test_bmi_c/cmake_build -S extern/test_bmi_c &&
		make -C extern/test_bmi_c/cmake_build &&
		# bmi_fortran
		cmake -B extern/test_bmi_fortran/cmake_build -S extern/test_bmi_fortran &&
		make -C extern/test_bmi_fortran/cmake_build
		

	# t-route
	# download

	# first, remove default t-route folder that comes with ngen, it is old
	cd extern
#	sudo rm -rf t-route
	mv t-route t-route_ORG
	# now clone the new t-route
	git clone --progress --single-branch --branch master http://github.com/NOAA-OWP/t-route.git

	cd t-route

	# compile and install
	./compiler.sh

	# copy build_ngen.sh and requirements.txt files to build folder
	cd $folder_name
	sudo mkdir BuildScripts
	sudo mv $rqr_in BuildScripts
	sudo cp ../build_ngen.sh BuildScripts

} | tee -a logs_${folder_name}/build_log.txt 2>&1

{	
	echo -e "\n\ntesting ngen bmi installs\n\n"
	cd $folder_name
#	./cmake_build/test/test_all &&
	./cmake_build/test/test_bmi_c &&
	./cmake_build/test/test_bmi_fortran || # &&
	./cmake_build/test/test_bmi_python ||
	exit 1

	# t-route
	echo -e "\n\ntesting t-route\n\n"
	source venv/bin/activate
	cd extern/t-route/test/LowerColorado_TX
	python -m nwm_routing -f test_AnA.yaml



	# t-route unit-test (changing syntax for consistency
#	echo -e "\n\nbuilding and testing test_routing_pybind\n\n"
	# make -C cmake_build test_routing_pybind &&
#	cmake --build cmake_build --target test_routing_pybind &&
# 	cmake -B cmake_build -S 
#	./cmake_build/test/test_routing_pybind ||
#		exit 1

} | tee -a logs_${folder_name}/test_log.txt 2>&1

# move logs to new build
mv logs_${folder_name} $folder_name

