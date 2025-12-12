#pragma once
#include "my_string.h"

void Telegram_getMe(const char* bot_token);
String Telegram_getUpdates(String url, int timeout, long int last_update);
void Curl_cleanup(void);
