#pragma once
#include "my_string.h"

typedef struct {
	String uid;
	String name;
	int gratz;
} User;

typedef struct {
	int size;
	int capacity;
	User* arr;
} UserArray;

int UserArray_Parse(UserArray* user_array, int* last_update);
User* UserArray_Get(UserArray* user_array, const char* uid);
void UserArray_Clear(UserArray* user_array);
bool UserArray_Add(UserArray* user_array, String uid, String name, int gratz);

void User_Print(User* u);

