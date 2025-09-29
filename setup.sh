#!/bin/bash

cmake -B build . -DCMAKE_BUILD_TYPE=Debug

cmake --build build --config Debug

#./gratzbot
valgrind --leak-check=full --track-origins=yes --dsymutil=yes --show-leak-kinds=all ./gratzbot
