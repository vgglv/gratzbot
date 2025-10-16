#include <stdio.h>
#include <curl/curl.h>
#include "requests.h"
#include "types.h"
#include "commands.h"
#include "config.h"
#include "users.h"
#include <stdlib.h>
#include <unistd.h>
#include "env.h"

int main(void) {
	load_env(".env");

	Config cfg;
	if (!Config_Parse(&cfg)) {
		printf("Error parsing config\n");
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

//	for (int i=0; i<commands.size; i++) {
//		printf("%d. ", i+1);
//		Commands_Print(&commands.arr[i]);
//	}

	UserArray user_array = {
		.size = 0,
		.arr = NULL,
		.capacity = 0
	};
	int last_update = 0;
	if (!UserArray_Parse(&user_array, &last_update)) {
		printf("Failed to parse users json. Maybe it does not exists?\n");
		return 1;
	}

	const char* bot_token = getenv("gratz_bot_api_key");
	UpdateList updates = Telegram_getUpdates(bot_token, 30, last_update);

//	while(true) {
//		sleep(cfg.sleep_time);
//		printf("Polling...\n");
//
//
//	}

//	User* user = UserArray_Get("7695735697");
//	if (user) {
//		User_Print(user);
//	} else {
//		printf("User not found\n");
//	}

	// is this really needed?
	Commands_Delete(&commands);
	String_Free(&cfg.url_route);
	UserArray_Clear(&user_array);

    return 0;
}

