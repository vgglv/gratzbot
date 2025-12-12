#pragma once
#include <stdbool.h>

typedef struct {
	char* data;
	int length;
} String;

String String_New(const char *src);
String String_Copy(String *src);
void String_Free(String *s);
bool String_Equals(const String *a, const String *b);
String String_Append(String a, String b);
bool StringIsOK(String str);
