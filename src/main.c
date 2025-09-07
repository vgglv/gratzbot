#include <stdio.h>
#include <curl/curl.h>
#include "Config.h"

int main(void) {
	Config cfg;
	if (parseConfig(&cfg) < 0) {
		fprintf(stderr, "Failed to parse config");
		return 1;
	}

	printf("Timeout: %d\n", cfg.request_timeout);
	printf("Url: %s\n", cfg.url_route);
	printf("Sleep time: %d\n", cfg.sleep_time);
    return 0;
}
