#!/bin/bash

# -Wall: prints out warnings
# -lm links the math library (libm) when compiling

gcc -Wall ./extern/topmodel/topmodel/src/main.c \
	./extern/topmodel/topmodel/src/bmi_topmodel.c \
	./extern/topmodel/topmodel/src/topmodel.c -o\
	run_topmodel_bmi -lm

./run_topmodel_bmi # ./Topmodel/topmodel_cat-12.run

