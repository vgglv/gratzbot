#include "env.h"
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "utils.h"

void load_env(const char *filename) {
	char* buffer = read_file(filename);
	int length = strlen(buffer);
	int buffer_size = 128;
	char key_buffer[buffer_size];
	char value_buffer[buffer_size];
	int key_pos = 0;
	int value_pos = 0;
	bool reading_key = false;
	bool reading_value = false;
	for (int i=0; i<length; i++) {
		if (buffer[i] == '=') {
			reading_key = false;
			reading_value = true;
			continue;
		}
		if (buffer[i] == '\n') {
			key_buffer[key_pos] = '\0';
			value_buffer[value_pos] = '\0';

			key_pos = 0;
			value_pos = 0;

			setenv(key_buffer, value_buffer, 1);

			memset(key_buffer, 0, buffer_size);
			memset(value_buffer, 0, buffer_size);
			continue;
		}
		if (key_pos == 0) {
			reading_key = true;
			reading_value = false;
		}
		if (reading_key) {
			if (isspace(buffer[i])) {
				continue;
			}
			key_buffer[key_pos] = buffer[i];
			key_pos++;
			continue;
		}
		if (reading_value) {
			if (isspace(buffer[i])) {
				continue;
			}
			value_buffer[value_pos] = buffer[i];
			value_pos++;
			continue;
		}
	}
	free(buffer);
}
