#pragma once

typedef struct Config {
	int sleep_time;
	int request_timeout;
	const char* url_route;
} Config;

int parseConfig(Config*);
