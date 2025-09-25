#include <stdio.h>
#include <curl/curl.h>
#include "cJSON.h"
#include <stdlib.h>
#include <string.h>
#include "types.h"
#include "utils.h"
#include "commands.h"

int parse_config(Config *config);

int main(void) {
	Config cfg;
	if (parse_config(&cfg) < 0) {
		return 1;
	} else {
		printf("Timeout: %d\n", cfg.request_timeout);
		printf("Url: %s\n", cfg.url_route.data);
		printf("Sleep time: %d\n", cfg.sleep_time);
	}

	CommandsArray commands;
	if (!Commands_Parse(&commands)) {
		printf("Error parsing commands\n");
		return 1;
	}

	for (int i=0; i<commands.size; i++) {
		for (int j=0; j<commands.arr[i].actions.size; j++) {
			Action* a = &commands.arr[i].actions.arr[j];
			printf("[%s][%s][%s]\n", a->type.data, a->value.data, a->send_to.data);
		}
	}

	// is this really needed?
	Commands_Delete(&commands);
	String_Free(&cfg.url_route);

    return 0;
}

int parse_config(Config* cfg) {
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
		cfg->url_route = String_New(url->valuestring);
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

