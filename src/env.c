#include "env.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

void load_env(const char *filename) {
	FILE *file = fopen(filename, "r");
	if (!file) {
		perror("fopen");
		return;
	}

	char line[512];
	while (fgets(line, sizeof(line), file)) {
		char *start = line;
		while (isspace((unsigned char)*start)) start++;

		if (*start == '#' || *start == '\0')
			continue;

		char *equal = strchr(start, '=');
		if (!equal) continue;

		*equal = '\0';
		char *key = start;
		char *value = equal + 1;

		key[strcspn(key, " \t\r\n")] = '\0';
		value[strcspn(value, " \t\r\n")] = '\0';

		setenv(key, value, 1); // overwrite = 1
	}

	fclose(file);
}
