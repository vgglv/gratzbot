package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
)

var users_data UsersData

func load_users_data_from_json() error {
	if _, err := os.Stat("users.json"); errors.Is(err, os.ErrNotExist) {
		err = write_users_data_to_json()
		if err != nil {
			return err
		}
	}
	content, err := os.ReadFile("users.json")
	if err != nil {
		return err
	}
	err = json.Unmarshal(content, &users_data)
	if err != nil {
		return err
	}
	if users_data.Users == nil {
		users_data.Users = make(map[int]UserInfo)
	}
	return nil
}

// saves current UsersData type to a users.json file
func write_users_data_to_json() error {
	if is_debug {
		fmt.Println("Writing json file...")
	}
	json, err := json.Marshal(users_data)
	if err != nil {
		return err
	}
	err = os.WriteFile("users.json", json, 0644)
	if err != nil {
		return err
	}
	return nil
}

func append_gratz_to_user(u User) {
	val, ok := users_data.Users[u.ID]
	if !ok {
		users_data.Users[u.ID] = UserInfo{1, u.FirstName}
		return
	}
	val.Gratz += 1
	val.Name = u.FirstName
	users_data.Users[u.ID] = val
}
