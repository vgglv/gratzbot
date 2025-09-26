#include <stdio.h>
#include <curl/curl.h>
#include "types.h"
#include "commands.h"
#include "config.h"

int main(void) {
	Config cfg;
	if (Config_Parse(&cfg) < 0) {
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
		printf("%d. ", i+1);
		Commands_Print(&commands.arr[i]);
	}

	// is this really needed?
	Commands_Delete(&commands);
	String_Free(&cfg.url_route);

    return 0;
}

