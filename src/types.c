#include "types.h"
#include "cJSON.h"
#include <stdio.h>

bool ParseUpdates(String data, UpdateArray *array) {
	printf("Output: %s\n", data.data);
	cJSON *root = cJSON_Parse(data.data);
	if (!root) {
		fprintf(stderr, "Failed to parse update json: %s\n", cJSON_GetErrorPtr());
		return false;
	}
	cJSON* ok_json = cJSON_GetObjectItem(root, "ok");
	if (!ok_json && !ok_json->valueint) {
		return false;
	}
	cJSON* result_json = cJSON_GetObjectItem(root, "result");
	cJSON* json_value;
	cJSON_ArrayForEach(json_value, result_json) {
		UpdateResult update = {0};
		cJSON* update_id_json = cJSON_GetObjectItem(json_value, "update_id");
		if (update_id_json) {
			update.update_id = update_id_json->valueint;
		}
		Message message = {0};
		cJSON* message_json = cJSON_GetObjectItem(json_value, "message");
		if (message_json) {
			cJSON* message_id_json = cJSON_GetObjectItem(message_json, "message_id");
			if (message_id_json) {
				message.message_id = message_id_json->valueint;
			}
			cJSON* text_json = cJSON_GetObjectItem(message_json, "text");
			if (text_json) {
				message.text = String_New(text_json->valuestring);
			}
		}
	}
	return true;
}
