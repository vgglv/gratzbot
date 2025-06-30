package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

var config Config

func parseConfigFromFile() error {
	config_file, err := os.ReadFile("assets/config.json")
	if err != nil {
		return err
	}
	if err = json.Unmarshal(config_file, &config); err != nil {
		return err
	}
	if err = godotenv.Load(); err != nil {
		return errors.New("Error loading .env file")
	}
	bot_token := os.Getenv("gratz_bot_api_key")
	if len(bot_token) == 0 {
		return errors.New("bot key is empty")
	}
	channel_id_str := os.Getenv("channel_id")
	if len(channel_id_str) == 0 {
		return errors.New("channel id is empty")
	}
	channel_id, err := strconv.Atoi(channel_id_str)
	if err != nil {
		return err
	}
	is_debug_str := os.Getenv("is_debug")
	var is_debug bool
	if is_debug_str == "true" {
		is_debug = true
	} else {
		is_debug = false
	}

	config.BotToken = bot_token
	config.ChannelId = channel_id
	config.IsDebug = is_debug
	config.UrlRoute = config.UrlRoute + config.BotToken
	if config.IsDebug {
		fmt.Printf("Loaded config: %+v\n", config)
	}
	return nil
}
