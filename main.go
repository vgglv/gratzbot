package main

import (
	"fmt"
	"time"
)

func main() {
	err := parse_config()
	if err != nil {
		fmt.Println(err)
		return
	}
	err = load_actions()
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
			time.Sleep(time.Duration(config.Sleep_time) * time.Second)
			continue
		}

		if len(updates) > 0 {
			for _, update := range updates {
				if update.Message.Chat.ID != config.channel_id && !config.is_debug {
					continue
				}
				if update.ID <= users_data.LastUpdate {
					continue
				}
				if config.is_debug {
					fmt.Printf("%+v\n", update)
				}
				perform_command_on_update(update)
			}
			last_index := len(updates) - 1
			last_element := updates[last_index]
			if users_data.LastUpdate != last_element.ID {
				users_data.LastUpdate = last_element.ID
			}
		}
		time.Sleep(time.Duration(config.Sleep_time) * time.Second)
	}
}
