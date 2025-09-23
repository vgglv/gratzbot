#!bin/bash

gcc -Wall -Wextra -g -O2 -I./src src/main.c src/cJSON.c -o gratzbot -lcurl -lz -lssl -lcrypto
