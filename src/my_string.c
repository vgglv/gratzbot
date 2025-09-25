#include "my_string.h"
#include <stdlib.h>

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
