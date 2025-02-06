package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"sync"
	"time"
)

var (
	http_client      = &http.Client{}
	http_client_once sync.Once
)

func getHttpClient() *http.Client {
	http_client_once.Do(func() {
		http_client.Timeout = time.Duration(config.Request_timeout) * time.Second
	})
	return http_client
}

func request_new_updates(offset int) ([]Update, error) {
	var buf bytes.Buffer
	params := RequestUpdatePayload{
		Offset:         strconv.Itoa(offset),
		Timeout:        strconv.Itoa(10),
		AllowedUpdates: []string{"message"},
	}

	encoder := json.NewEncoder(&buf)
	err := encoder.Encode(params)
	if err != nil {
		return nil, err
	}
	url := config.Url_route + "/getUpdates"
	req, err := http.NewRequest(http.MethodPost, url, &buf)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := getHttpClient().Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != 200 {
		return nil, &CustomError{
			message: "status was not equal 200",
		}
	}
	var tg_response UpdateResponsePayload
	err = json.Unmarshal(body, &tg_response)
	if err != nil {
		return nil, err
	}
	return tg_response.Result, nil
}

func make_reaction_request(message_id int, chat_id int, reaction []ReactionType) error {
	if message_id == 0 {
		return &CustomError{"[Reaction] message_id was 0"}
	}
	if config.is_debug {
		fmt.Println("Sending reaction")
	}
	var buf bytes.Buffer
	params := map[string]string{
		"chat_id":    strconv.Itoa(chat_id),
		"message_id": strconv.Itoa(message_id),
	}
	data, err := json.Marshal(reaction)
	if err != nil {
		return err
	}
	params["reaction"] = string(data)

	encoder := json.NewEncoder(&buf)
	err = encoder.Encode(params)
	if err != nil {
		return err
	}
	url := config.Url_route + "/setMessageReaction"
	req, err := http.NewRequest(http.MethodPost, url, &buf)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := getHttpClient().Do(req)
	if err != nil {
		return err
	}
	resp.Body.Close()
	return nil
}

func make_request_send_message_to_chat(chat_id int, text string) error {
	var buf bytes.Buffer
	params := SendMessagePayload{
		ChatId: strconv.Itoa(chat_id),
		Text:   text,
	}
	encoder := json.NewEncoder(&buf)
	err := encoder.Encode(params)
	if err != nil {
		return err
	}
	url := config.Url_route + "/sendMessage"
	req, err := http.NewRequest(http.MethodPost, url, &buf)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := getHttpClient().Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	var tg_response SendMessageResponsePayload
	err = json.Unmarshal(body, &tg_response)
	if err != nil {
		fmt.Println("Error serializing response:\n", err)
		return err
	}
	return nil
}
