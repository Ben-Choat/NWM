#!/bin/bash



rm -rf extern/topmodel/cmake_build

cmake -B extern/topmodel/cmake_build -S extern/topmodel &&
	make -C extern/topmodel/cmake_build
