#pragma once
#include "my_string.h"
#include <stdbool.h>

typedef enum {
	CONDITION_NONE         = 0,
	CONDITION_REPLY        = 1 << 0, // 0001
	CONDITION_NOT_HIMSELF  = 1 << 1, // 0010
	CONDITION_HIMSELF      = 1 << 2, // 0011
	CONDITION_BOT_COMMAND  = 1 << 3, // 0100
	CONDITION_SOLO_MESSAGE = 1 << 4, // 0101
	CONDITION_BOT          = 1 << 5, // 0110
} ConditionFlags;

typedef struct {
	int sleep_time;
	int request_timeout;
	String url_route;
} Config;

typedef struct {
	String type;
	String value;
	String send_to;
	String value_on_fail;
	int probability;
} Action;

typedef struct {
	Action* arr;
	int size;
} ActionsArray;

typedef struct {
	String text_contains;
	int condition;
	ActionsArray actions;
} Command;

typedef struct {
	Command* arr;
	int size;
} CommandsArray;

typedef struct {
	int message_id;
	unsigned long date;
	String text;
} Message;

typedef struct {
	unsigned long update_id;
	Message message;
} UpdateResult;

typedef struct {
	UpdateResult* arr;
	int size;
} UpdateArray;

bool ParseUpdates(String data, UpdateArray *array);
