#!bin/bash

# this is release
#gcc -Wall -Wextra -g -O2 -I./src src/main.c src/cJSON.c -o gratzbot -lcurl -lz -lssl -lcrypto

# this is debug
gcc -Wall -Wextra -g -I./src src/main.c src/cJSON.c -o gratzbot -lcurl -lz -lssl -lcrypto
