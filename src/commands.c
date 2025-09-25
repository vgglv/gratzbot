#include "commands.h"
#include "utils.h"
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

bool Commands_Parse(CommandsArray* cmd_arr) {
	Commands_Delete(cmd_arr);
	char *commands_file = read_file("assets/commands.json");
	if (!commands_file) {
		return NULL;
	}
	cJSON *root = cJSON_Parse(commands_file);
	if (!root) {
		fprintf(stderr, "Failed to parse commands json: %s\n", cJSON_GetErrorPtr());
		free(commands_file);
		return NULL;
	}
	cJSON *row = NULL;
	int commands_size = cJSON_GetArraySize(root);
	cmd_arr->size = commands_size;
	cmd_arr->arr = malloc(cmd_arr->size * sizeof(Command));
	int commands_pos = 0;
	cJSON_ArrayForEach(row, root) {
		cJSON *text_contains_json = cJSON_GetObjectItem(row, "text_contains");
		const char* text_contains = text_contains_json->valuestring;
		Command* current_cmd = &cmd_arr->arr[commands_pos];
		current_cmd->text_contains = String_New(text_contains);
		cJSON *conditions = cJSON_GetObjectItem(row, "conditions");
		cJSON *condition_json = NULL;
		current_cmd->condition = CONDITION_NONE;
		cJSON_ArrayForEach(condition_json, conditions) {
			current_cmd->condition |= condition_flag_from_string(condition_json->valuestring);
		}
		cJSON *actions_json = cJSON_GetObjectItem(row, "actions");
		cJSON *actions_row_json = NULL;
		int actions_size = cJSON_GetArraySize(actions_json);
		if (actions_size > 0) {
			current_cmd->actions.arr = malloc(actions_size * sizeof(Action));
			current_cmd->actions.size = actions_size;
			int action_pos = 0;
			cJSON_ArrayForEach(actions_row_json, actions_json) {
				cJSON *type_json = cJSON_GetObjectItem(actions_row_json, "type");
				cJSON *send_to = cJSON_GetObjectItem(actions_row_json, "send_to");
				cJSON *value_json = cJSON_GetObjectItem(actions_row_json, "value");

				Action* current_action = &current_cmd->actions.arr[action_pos];
				current_action->type = String_New(type_json->valuestring);

				if (value_json) {
					current_action->value = String_New(value_json->valuestring);
				}

				if (send_to) {
					current_action->send_to = String_New(send_to->valuestring);
				}
				action_pos++;
			}
		}
		commands_pos++;
	}
	cJSON_Delete(root);
	free(commands_file);
	return true;
}

void Commands_Delete(CommandsArray* cmds) {
	for (int i=0; i<cmds->size; i++) {
		String_Free(&cmds->arr[i].text_contains);
		for (int j=0; j<cmds->arr[i].actions.size; j++) {
			String_Free(&cmds->arr[i].actions.arr[j].value);
			String_Free(&cmds->arr[i].actions.arr[j].send_to);
			String_Free(&cmds->arr[i].actions.arr[j].type);
		}
		free(cmds->arr[i].actions.arr);
		cmds->arr[i].actions.arr = NULL;
		cmds->arr[i].actions.size = 0;
	}

	free(cmds->arr);
	cmds->arr = NULL;
	cmds->size = 0;
}

