package main

import (
	"encoding/json"
	"fmt"
	"os"
)

var usersDB UsersData

func Users_loadDB() error {
	content, err := os.ReadFile("users.json")
	if err != nil {
		return err
	}
	err = json.Unmarshal(content, &usersDB)
	if err != nil {
		return err
	}
	fmt.Println(usersDB)
	return nil
}

// saves current UsersData type to a users.json file
func Users_saveDB() error {
	json, err := json.Marshal(usersDB)
	if err != nil {
		return err
	}
	err = os.WriteFile("users.json", json, 0644)
	if err != nil {
		return err
	}
	return nil
}

