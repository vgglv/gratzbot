package main

import (
	"fmt"
	"time"
)

func main() {
	err := ParseEnvVariables()
	if err != nil {
		fmt.Println(err)
		return
	}
	err = load_users_data_from_json()
	if err != nil {
		fmt.Println(err)
		return
	}
	for {
		updates, err := request_new_updates(users_data.LastUpdate)
		if err != nil {
			fmt.Println("Some error happened:\n", err)
			time.Sleep(5 * time.Second)
			continue
		}

		if len(updates) > 0 {
			process_telegram_updates(updates, users_data.LastUpdate)
			last_index := len(updates) - 1
			last_element := updates[last_index]
			if users_data.LastUpdate != last_element.ID {
				users_data.LastUpdate = last_element.ID
				err := write_users_data_to_json()
				if err != nil {
					fmt.Println("Error writing json data", err)
				}
			}
		}
		time.Sleep(5 * time.Second)
	}
}
