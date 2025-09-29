#include "config.h"
#include "utils.h"
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

bool Config_Parse(Config* cfg) {
	char *configBytes = read_file("assets/config.json");
	if (!configBytes) {
		return false;
	}
	
	cJSON *root = cJSON_Parse(configBytes);
	if (!root) {
		fprintf(stderr, "Failed to parse json: %s\n", cJSON_GetErrorPtr());
		free(configBytes);
		return false;
	}

	cJSON *sleep_time = cJSON_GetObjectItemCaseSensitive(root, "sleep_time");
	if (cJSON_IsNumber(sleep_time)) {
		cfg->sleep_time = sleep_time->valueint;
	} else {
		fprintf(stderr, "Failed to parse json: 'sleep_time'\n");
		free(configBytes);
		return false;
	}

	cJSON *timeout = cJSON_GetObjectItemCaseSensitive(root, "request_timeout");
	if (cJSON_IsNumber(timeout)) {
		cfg->request_timeout = timeout->valueint;
	} else {
		fprintf(stderr, "Failed to parse json: 'request_timeout'\n");
		free(configBytes);
		return false;
	}

	cJSON *url = cJSON_GetObjectItemCaseSensitive(root, "url_route");
	if (cJSON_IsString(url) && url->valuestring != NULL) {
		cfg->url_route = String_New(url->valuestring);
		//cfg->url_route = url->valuestring;
	} else {
		fprintf(stderr, "Failed to parse json: 'url_route'\n");
		free(configBytes);
		return false;
	}
	free(configBytes);
	cJSON_Delete(root);

	return true;
}

