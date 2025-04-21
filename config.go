package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

var config Config

type EnvError struct {
	msg string
}

func (e *EnvError) Error() string {
	return e.msg
}

func parse_config() error {
	config_file, err := os.ReadFile("assets/config.json")
	if err != nil {
		return err
	}
	err = json.Unmarshal(config_file, &config)
	if err != nil {
		return err
	}
	err = godotenv.Load()
	if err != nil {
		return &EnvError{"Error loading .env file"}
	}
	bot_token := os.Getenv("gratz_bot_api_key")
	if len(bot_token) == 0 {
		return &EnvError{"bot key is empty"}
	}
	channel_id_str := os.Getenv("channel_id")
	if len(channel_id_str) == 0 {
		return &EnvError{"channel id is empty"}
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

	config.bot_token = bot_token
	config.channel_id = channel_id
	config.is_debug = is_debug
	config.Url_route = config.Url_route + config.bot_token
	fmt.Printf("Loaded config: %+v\n", config)
	return nil
}
