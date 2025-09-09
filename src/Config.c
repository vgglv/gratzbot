#include "Config.h"
#include "Utils.h"
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

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
		cfg->url_route = url->valuestring;
	} else {
		fprintf(stderr, "Failed to parse json: 'url_route'\n");
		free(configBytes);
		return -1;
	}
	free(configBytes);
	cJSON_Delete(root);

	return 1;
}
