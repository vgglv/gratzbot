#include "requests.h"
#include <curl/curl.h>
#include <curl/easy.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "my_string.h"

bool is_inited = false;
CURL *curl = NULL;

size_t write_callback(void *data, size_t size, size_t nmemb, void *userp) {
	size_t realsize = size * nmemb;
	String *str = (String *)userp;

	char *ptr = realloc(str->data, str->length + realsize + 1);
	if (ptr == NULL) {
		fprintf(stderr, "Out of memory writing callback from cURL\n");
		return 0;
	}

    str->data = ptr;
    memcpy(&(str->data[str->length]), data, realsize);
    str->length += realsize;
    str->data[str->length] = '\0';

    return realsize;
}

void Curl_Initialize(void) {
	if (is_inited) {
		return;
	}
	curl_global_init(CURL_GLOBAL_DEFAULT);
	curl = curl_easy_init();
	if (!curl) {
		fprintf(stderr, "Failed to initialize CURL\n");
		return;
	}
	is_inited = true;
}

void Curl_cleanup(void) {
	curl_easy_cleanup(curl);
}

void Telegram_getMe(const char* bot_token) {
	Curl_Initialize();
	char url[512];
	snprintf(url, sizeof(url), "https://api.telegram.org/bot%s/getMe", bot_token);
	String output = {0};
	curl_easy_setopt(curl, CURLOPT_URL, url);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void*) &output);
	CURLcode res = curl_easy_perform(curl);
	if (res == CURLE_OK) {
		printf("Telegram_getMe response:\n%s\n", output.data);
	} else {
		fprintf(stderr, "[ERROR][Telegram_getMe] curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
	}
}

void Telegram_getUpdates(const char* bot_token, int timeout, long int last_update) {
	Curl_Initialize();
	char url[512];
	snprintf(url, sizeof(url), "https://api.telegram.org/bot%s/getUpdates?timeout=%d&offset=%ld", bot_token, timeout, last_update);

	String output = {0};
	curl_easy_setopt(curl, CURLOPT_URL, url);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void*) &output);
	CURLcode res = curl_easy_perform(curl);
	if (res == CURLE_OK) {
		printf("Telegram_getUpdate response:\n%s\n", output.data);
	} else {
		fprintf(stderr, "[ERROR][Telegram_getUpdates] curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
	}

	String_Free(&output);
}
