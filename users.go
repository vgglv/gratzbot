package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
)

var users_data UsersData

func loadUsersDataFromJson() error {
	if _, err := os.Stat("users.json"); errors.Is(err, os.ErrNotExist) {
		err = writeUsersDataToJson()
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
func writeUsersDataToJson() error {
	if config.IsDebug {
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

func appendGratzToUser(u User) {
	val, ok := users_data.Users[u.ID]
	if !ok {
		users_data.Users[u.ID] = UserInfo{1, u.FirstName}
		err := writeUsersDataToJson()
		if err != nil {
			fmt.Println("Error saving json:", err)
		}
		return
	}
	val.Gratz += 1
	val.Name = u.FirstName
	users_data.Users[u.ID] = val
	if config.IsDebug {
		fmt.Printf("Appending gratz to user %v, amount: %v\n", u.FirstName, val.Gratz)
	}
	err := writeUsersDataToJson()
	if err != nil {
		fmt.Println("Error saving json:", err)
	}
}
