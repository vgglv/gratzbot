#include <stdio.h>
#include <curl/curl.h>
#include <cJSON.h>
#include <stdlib.h>
#include <string.h>

typedef struct Config {
	int sleep_time;
	int request_timeout;
	char* url_route;
} Config;

typedef struct Command {
	
} Command;

char* read_file(const char* filename);
int parseConfig(Config*);

int main(void) {
	Config cfg;
	if (parseConfig(&cfg) < 0) {
		return 1;
	} else {
		printf("Timeout: %d\n", cfg.request_timeout);
		printf("Url: %s\n", cfg.url_route);
		printf("Sleep time: %d\n", cfg.sleep_time);
	}

    return 0;
}

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

int parseConfig(Config* cfg) {
	char *configBytes = read_file("assets/config.json");
	if (!configBytes) {
		return -1;
	}
	
	cJSON *root = cJSON_Parse(configBytes);
	if (!root) {
		fprintf(stderr, "Failed to parse json: %s\n", cJSON_GetErrorPtr());
		free(configBytes);
		return -1;
	}

	cJSON *sleep_time = cJSON_GetObjectItemCaseSensitive(root, "sleep_time");
	if (cJSON_IsNumber(sleep_time)) {
		cfg->sleep_time = sleep_time->valueint;
	} else {
		fprintf(stderr, "Failed to parse json: 'sleep_time'\n");
		free(configBytes);
		return -1;
	}

	cJSON *timeout = cJSON_GetObjectItemCaseSensitive(root, "request_timeout");
	if (cJSON_IsNumber(timeout)) {
		cfg->request_timeout = timeout->valueint;
	} else {
		fprintf(stderr, "Failed to parse json: 'request_timeout'\n");
		free(configBytes);
		return -1;
	}

	cJSON *url = cJSON_GetObjectItemCaseSensitive(root, "url_route");
	if (cJSON_IsString(url) && url->valuestring != NULL) {
		cfg->url_route = malloc(strlen(url->valuestring) + 1);
		strcpy(cfg->url_route, url->valuestring);
		//cfg->url_route = url->valuestring;
	} else {
		fprintf(stderr, "Failed to parse json: 'url_route'\n");
		free(configBytes);
		return -1;
	}
	free(configBytes);
	cJSON_Delete(root);

	return 1;
}
