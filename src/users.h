#pragma once
#include "my_string.h"
#include <stdlib.h>

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

bool UserArray_Parse(void);
User* UserArray_Get(const char* uid);
void UserArray_Clear(void);

bool User_Add(String uid, String name, int gratz);
void User_Print(User* u);
void User_Clear(void);
