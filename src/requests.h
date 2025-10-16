#pragma once

void Telegram_getMe(const char* bot_token);
void Telegram_getUpdates(const char* bot_token, int timeout, long int last_update);
void Curl_cleanup(void);
