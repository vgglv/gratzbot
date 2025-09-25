#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "types.h"

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

int condition_flag_from_string(const char *s) {
	if (strcmp(s, "reply") == 0) return CONDITION_REPLY;
	if (strcmp(s, "not_himself") == 0) return CONDITION_NOT_HIMSELF;
	if (strcmp(s, "himself") == 0) return CONDITION_HIMSELF;
	if (strcmp(s, "bot_command") == 0) return CONDITION_BOT_COMMAND;
	if (strcmp(s, "bot") == 0) return CONDITION_BOT;
	if (strcmp(s, "solo_message") == 0) return CONDITION_SOLO_MESSAGE;
	return CONDITION_NONE;
}
