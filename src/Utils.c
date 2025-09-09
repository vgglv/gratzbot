#include "Utils.h"
#include <stdio.h>
#include <stdlib.h>

char* read_file(const char* filename) {
	FILE *f = fopen(filename, "rb");
	if (!f) {
		perror("fopen");
		return NULL;
	}

	fseek(f, 0, SEEK_END);
	long len = ftell(f);
	rewind(f);

	char *result = malloc(len + 1);
	if (!result) {
		perror("malloc");
		fclose(f);
		return NULL;
	}

	if (fread(result, 1, len, f) != (size_t)len) {
		perror("fread");
		free(result);
		fclose(f);
		return NULL;
	}

	result[len] = '\0';

	fclose(f);

	return result;
}
