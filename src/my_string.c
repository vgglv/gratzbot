#include "my_string.h"
#include <stdlib.h>

String String_Copy(String *src) {
	String new_str;
	new_str.length = src->length;
	new_str.data = malloc(src->length + 1);
	for (int i=0; i<src->length;i++) {
		new_str.data[i] = src->data[i];
	}
	new_str.data[new_str.length] = '\0';
	return new_str;
}

String String_New(const char *src) {
	String s;
	s.length = 0;
	while (src[s.length] != '\0') {
		s.length++;
	}
	s.data = malloc(s.length + 1);
	for (int i = 0; i < s.length; i++) {
		s.data[i] = src[i];
	}
	s.data[s.length] = '\0';
	return s;
}

void String_Free(String *s) {
	if (!s) {
		return;
	}
	if (s->length == 0) {
		return;
	}
	if (!s->data) {
		return;
	}
	free(s->data);
	s->data = NULL;
	s->length = 0;
}

bool String_Equals(const String *a, const String *b) {
	if (a->length != b->length) return false;
	for (int i = 0; i < a->length; i++) {
		if (a->data[i] != b->data[i]) return false;
	}
	return true;
}

String String_Append(String a, String b) {
	String result = {0};
	int total_length = a.length + b.length;
	result.data = malloc(total_length + 1);
	for (int i=0; i<a.length; i++) {
		result.data[i] = a.data[i];
	}
	int offset = a.length;
	for (int i=0; i<b.length;i++) {
		result.data[i+offset] = b.data[i];
	}
	result.data[total_length] = '\0';
	return result;
}

bool StringIsOK(String str) {
	return str.length > 0 && str.data != NULL;
}
