package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
)

func Telegram_sendMessage(chat_id int, text string) error {
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
	url := "https://api.telegram.org/bot" + bot_token + "/sendMessage"
	req, err := http.NewRequest(http.MethodPost, url, &buf)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
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

func Telegram_setMessageReaction(message_id int, chat_id int, reaction []ReactionType) error {
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
	url := "https://api.telegram.org/bot" + bot_token + "/setMessageReaction"
	req, err := http.NewRequest(http.MethodPost, url, &buf)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	resp.Body.Close()
	return nil
}

func Telegram_requestUpdates(offset int) ([]Update, error) {
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
	url := "https://api.telegram.org/bot" + bot_token + "/getUpdates"
	req, err := http.NewRequest(http.MethodPost, url, &buf)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != 200 {
		return nil, err
	}
	var tg_response UpdateResponsePayload
	err = json.Unmarshal(body, &tg_response)
	if err != nil {
		fmt.Println("Error serializing response:\n", err)
		return nil, err
	}
	//fmt.Println(string(body))
	return tg_response.Result, nil
}
