#!/bin/bash

# bchoat 2023/07/19

# used to build ngen in Ubuntu 22.04

# Script builds and test ngen. Define a folder name which will be used for the home 
# directory for the build as well as for labeling a folder where the build and
# test logs will be saved.

# options should be edited around line 120, where cmake is used to build ngen.


# provide name for folder that will hold this ngen version
folder_name="ngen20230719"

mkdir logs_${folder_name}

# define python location
# export Python_NumPy_INCLUDE_DIRS=/home/bchoat/Projects/NWM_NGEN/${folder_name}/.venv/lib/python3.10/site-packages
export Python_NumPy_INCLUDE_DIR=/home/bchoat/Projects/NWM_NGEN/${folder_name}/.venv/lib/python3.10/site-packages


{
	echo "building in $folder_name"
	# install libraries
	echo -e "\n\ninstalling libraries into bash\n\n"
	sudo apt-get update &&
		sudo apt install cmake &&
		sudo apt-get install g++ &&
		sudo apt install gfortran &&
		sudo apt-get install python3-dev &&
		sudo apt install python3 &&
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
	# git submodule update --init --recursive --remote -- extern/t-route
	
	
	
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
	echo -e "\n\nbuliding noah-owp and iso_c_fortran and adding netcfd libraries\n\n"
	cmake -B extern/noah-owp-modular/cmake_build -S extern/noah-owp-modular \
		-DnetCDF_INCLUDE_DIR=/usr/include/ -DnetCDF_MOD_PATH=/usr/include/ \
		-DnetCDF_FORTRAN_LIB=/usr/lib/x86_64_linux_gnu/libnetcdff.so &&
		make -C extern/noah-owp-modular/cmake_build &&
		cmake -B extern/iso_c_fortran_bmi/cmake_build -S extern/iso_c_fortran_bmi &&
		make -C extern/iso_c_fortran_bmi/cmake_build ||
		exit 1
	
	# create python virtual environment
	echo -e "\n\ninstalling python libraries w/.venv\n\n"
	mkdir .venv &&
		python3 -m venv .venv &&
		source .venv/bin/activate &&
		pip install numpy || # &&
		# pip install -U pip setuptools cython dask &&
		# pip install deprecated &&
		# pip install bmipy &&
		# pip install tables && #   --hdf5=/usr/lib &&
		# pip install pydantic || # &&
#		pip install pybind11 ||
		exit 1		
	
	
	# compiling t-route
	echo -e "\n\ninstalling/building t-route python libs\n\n"
	pip install -e extern/t-route/src/ngen_routing/ &&
		pip install -e extern/t-route/src/nwm_routing/ ||
		exit 1
	
	
	
	echo -e "\n\nprepending .venv directory to PATH\n\n"
	echo -e "Set assuming PWD = ${PWD}\n\n"
	export PATH="${PWD}/.venv/bin:$PATH"

	echo $PATH

	
#	echo -e "\n\nediting t-rout code as needed\n\n"
#	cd extern/t-route/src/python_routing_v02
#	sed -i '27 i export LIBRARY_PATH=/usr:$LIBRARY_PATH' compiler.sh
#	sed -i '28 i export NETCDFINC=/usr/' compiler.sh
#	sed -i 's/F90="gfortran"/F90=gfortran .\/compiler.sh/' compiler.sh
	
#	cd ../../../../
	
	
#  sed -i "s|^\s*find_package(Python|set(Python_EXECUTABLE \"${PWD}/.venv/bin/python\")\nfind_package(Python|" CMakeLists.txt

	
	# compile ngen -Add boost path -with routing
	echo -e "\n\nbuliding ngen\n\n"
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
	
		cmake -B extern/test_bmi_c/cmake_build -S extern/test_bmi_c &&
		make -C extern/test_bmi_c/cmake_build &&
		cmake -B extern/test_bmi_fortran/cmake_build -S extern/test_bmi_fortran &&
		make -C extern/test_bmi_fortran/cmake_build
		

} | tee -a logs_${folder_name}/build_log.txt 2>&1

{	
	echo -e "\n\ntesting install\n\n"
	cd $folder_name
#	./cmake_build/test/test_all &&
	./cmake_build/test/test_bmi_c &&
		./cmake_build/test/test_bmi_fortran ||
		exit 1


	# t-route unit-test (changing syntax for consistency
#	echo -e "\n\nbuilding and testing test_routing_pybind\n\n"
	# make -C cmake_build test_routing_pybind &&
#	cmake --build cmake_build --target test_routing_pybind &&
# 	cmake -B cmake_build -S 
#	./cmake_build/test/test_routing_pybind ||
#		exit 1

} | tee -a logs_${folder_name}/test_log.txt 2>&1


