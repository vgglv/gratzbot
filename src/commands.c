#include "commands.h"
#include "types.h"
#include "utils.h"
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

bool Commands_Parse(CommandsArray* cmd_arr) {
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
				cJSON *send_to_json = cJSON_GetObjectItem(actions_row_json, "send_to");
				cJSON *value_json = cJSON_GetObjectItem(actions_row_json, "value");
				cJSON *value_on_fail_json = cJSON_GetObjectItem(actions_row_json, "value_on_fail");
				cJSON *probability_json = cJSON_GetObjectItem(actions_row_json, "probability");

				Action* current_action = &current_cmd->actions.arr[action_pos];
				current_action->type = String_New(type_json->valuestring);

				if (value_json) {
					current_action->value = String_New(value_json->valuestring);
				}

				if (send_to_json) {
					current_action->send_to = String_New(send_to_json->valuestring);
				}

				if (value_on_fail_json) {
					current_action->value_on_fail = String_New(value_on_fail_json->valuestring);
				}

				if (probability_json) {
					current_action->probability = probability_json->valueint;
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
			String_Free(&cmds->arr[i].actions.arr[j].value_on_fail);
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

void Commands_Print(Command* cmd) {
	printf("Command:\n");
	if (cmd->text_contains.length > 0) {
		printf("  Text contains: %s\n", cmd->text_contains.data);
	}
	if (cmd->condition & CONDITION_BOT) {
		printf("  Condition: BOT\n");
	}
	if (cmd->condition & CONDITION_BOT_COMMAND) {
		printf("  Condition: BOT_COMMAND\n");
	}
	if (cmd->condition & CONDITION_HIMSELF) {
		printf("  Condition: HIMSELF\n");
	}
	if (cmd->condition & CONDITION_REPLY) {
		printf("  Condition: REPLY\n");
	}
	if (cmd->condition & CONDITION_NOT_HIMSELF) {
		printf("  Condition: NOT_HIMSELF\n");
	}
	if (cmd->condition & CONDITION_SOLO_MESSAGE) {
		printf("  Condition: SOLO_MESSAGE\n");
	}

	if (cmd->actions.size > 0) {
		printf("  Actions:\n");
		for (int j=0; j<cmd->actions.size; j++) {
			Action* a = &cmd->actions.arr[j];
			printf("    Type: %s, value: %s, send_to: %s, value_on_fail: %s, probability: %d\n", a->type.data, a->value.data, a->send_to.data, a->value_on_fail.data, a->probability);
		}
	}
}
