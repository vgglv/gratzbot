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
	err = Stocks_loadDB()
	if err != nil {
		fmt.Println(err)
		return
	}
	err = Stocks_saveBackupDB()
	if err != nil {
		fmt.Println(err)
	}
	offset := 0
	for {
		updates, err := Telegram_requestUpdates(offset)
		if err != nil {
			fmt.Println("Some error happened:\n", err)
			time.Sleep(5 * time.Second)
			continue
		}

		if len(updates) > 0 {
			ResponseHandler_processUpdates(updates, offset)
			last_index := len(updates) - 1
			last_element := updates[last_index]
			offset = last_element.ID
		}
		time.Sleep(5 * time.Second)
	}
}
