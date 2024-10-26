package main

import (
	"errors"
	"fmt"
	"os"
)

var bot_token string

func ParseEnvVariables() error {
	bot_token = os.Getenv("gratz_bot_api_key")
	if len(bot_token) == 0 {
		return errors.New("Bot key is empty!")
	}
	fmt.Printf("Bot key: %v\n", bot_token)
	return nil
}
