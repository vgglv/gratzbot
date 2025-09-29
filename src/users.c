#include "users.h"
#include "utils.h"
#include "cJSON.h"
#include <stdio.h>
#include <string.h>

UserArray user_array;

bool UserArray_Parse(void) {
	char *users_file = read_file("users.json");
	if (!users_file) {
		return false;
	}
	cJSON *root = cJSON_Parse(users_file);
	if (!root) {
		fprintf(stderr, "Failed to parse user json: %s\n", cJSON_GetErrorPtr());
		free(users_file);
		return false;
	}
	cJSON *last_update_json = cJSON_GetObjectItem(root, "last_update");
	cJSON *users_json = cJSON_GetObjectItem(root, "Users");
	int last_update = last_update_json->valueint;
	cJSON* row_json = NULL;
	cJSON_ArrayForEach(row_json, users_json) {
		cJSON *gratz_json = cJSON_GetObjectItem(row_json, "gratz");
		cJSON *name_json = cJSON_GetObjectItem(row_json, "name");
		const char *user_id = row_json->string;

		String uid = String_New(user_id);
		String name = String_New(name_json->valuestring);
		int gratz = gratz_json->valueint;
		if (!User_Add(uid, name, gratz)) {
			String_Free(&uid);
			String_Free(&name);
			continue;
		}

		User_Add(uid, name, gratz);
	}
	cJSON_Delete(root);
	free(users_file);

	return true;
}

bool User_Add(String uid, String name, int gratz) {
	for (int i=0; i<user_array.size;i++) {
		if (String_Equals(&user_array.arr[i].uid, &uid)) {
			// user already exists
			return false;
		}
	}
	if (user_array.size >= user_array.capacity) {
		int new_capacity = (user_array.capacity == 0) ? 4 : user_array.capacity * 2;
		User* new_arr = realloc(user_array.arr, new_capacity * sizeof(User));
		if (!new_arr) {
			// i dont know wtf to do here
			return false;
		}
		user_array.arr = new_arr;
		user_array.capacity = new_capacity;
	}
	User* user = &user_array.arr[user_array.size];

	user->uid = uid;
	user->name = name;
	user->gratz = gratz;

	user_array.size++;
	return true;
}

User* UserArray_Get(const char* uid) {
	for (int i=0; i<user_array.size;i++) {
		if (strcmp(user_array.arr[i].uid.data, uid) == 0) {
			return &user_array.arr[i];
		}
	}
	return NULL;
}

void UserArray_Clear(void) {
	for (int i=0; i<user_array.size;i++) {
		String_Free(&user_array.arr[i].name);
		String_Free(&user_array.arr[i].uid);
	}
	free(user_array.arr);
}

void User_Print(User* u) {
	printf("[%s] gratz: %d, name: %s\n", u->uid.data, u->gratz, u->name.data);
}
