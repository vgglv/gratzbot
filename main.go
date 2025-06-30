package main

import (
	"fmt"
	"time"
)

func main() {
	if err := parseConfigFromFile(); err != nil {
		fmt.Println(err)
		return
	}
	if err := loadActionsFromFile(); err != nil {
		fmt.Println(err)
		return
	}
	if err := loadUsersDataFromJson(); err != nil {
		fmt.Println(err)
		return
	}
	for {
		updates, err := requestNewUpdates(users_data.LastUpdate)
		if err != nil {
			fmt.Println(err)
			time.Sleep(time.Duration(config.SleepTime) * time.Second)
			continue
		}

		if len(updates) > 0 {
			for _, update := range updates {
				if update.Message.Chat.Id != config.ChannelId && !config.IsDebug {
					continue
				}
				if update.UpdateId <= users_data.LastUpdate {
					continue
				}
				if config.IsDebug {
					fmt.Printf("%+v\n", update)
				}
				processCommandOnUpdate(update)
			}
			last_index := len(updates) - 1
			last_element := updates[last_index]
			if users_data.LastUpdate != last_element.UpdateId {
				users_data.LastUpdate = last_element.UpdateId
			}
		}
		time.Sleep(time.Duration(config.SleepTime) * time.Second)
	}
}
