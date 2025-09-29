#include <stdio.h>
#include <curl/curl.h>
#include "types.h"
#include "commands.h"
#include "config.h"
#include "users.h"

int main(void) {
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

	if (!UserArray_Parse()) {
		printf("Failed to parse users json. Maybe it does not exists?\n");
		return 1;
	}

//	User* user = UserArray_Get("7695735697");
//	if (user) {
//		User_Print(user);
//	} else {
//		printf("User not found\n");
//	}

	// is this really needed?
	Commands_Delete(&commands);
	String_Free(&cfg.url_route);
	UserArray_Clear();

    return 0;
}

