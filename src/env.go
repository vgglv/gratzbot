package main

import (
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

var bot_token string
var channel_id int
var is_debug bool

func ParseEnvVariables() error {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file!")
	}
	bot_token = os.Getenv("gratz_bot_api_key")
	if len(bot_token) == 0 {
		return errors.New("bot key is empty")
	}
	channel_id_str := os.Getenv("channel_id")
	if len(channel_id_str) == 0 {
		return errors.New("channel id is empty")
	}
	channel_id, err = strconv.Atoi(channel_id_str)
	if err != nil {
		return err
	}
	is_debug_str := os.Getenv("is_debug")
	if is_debug_str == "true" {
		is_debug = true
	} else {
		is_debug = false
	}
	fmt.Printf("Bot key: %v\n", bot_token)
	fmt.Printf("Channel id: %v\n", channel_id)
	fmt.Printf("Debug: %v\n", is_debug)
	return nil
}
