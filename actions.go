package main

import (
	"encoding/json"
	"fmt"
	"os"
	"slices"
	"sort"
	"strconv"
)

var commandsDB []Command

func load_actions() error {
	commands_file, err := os.ReadFile("assets/commands.json")
	if err != nil {
		return err
	}
	err = json.Unmarshal(commands_file, &commandsDB)
	if err != nil {
		return err
	}
	fmt.Printf("%+v\n", commandsDB)
	return nil
}

func perform_command_on_update(u Update) {
	for _, command := range commandsDB {
		if !contains_exact_word(u.Message.Text, command.Text_contains) {
			continue
		}
		var when_ok bool = true
		for _, w := range command.When {
			if !check_if_when_fulfilled(w, u) {
				when_ok = false
				break
			}
		}
		if !when_ok {
			continue
		}
		for _, action := range command.Actions {
			perform_action(action, u)
		}
	}
}

func check_if_when_fulfilled(when WhenType, u Update) bool {
	switch when {
	case WhenType_Himself:
		return u.Message.From.ID == u.Message.ReplyMsg.From.ID
	case WhenType_NotHimself:
		return u.Message.From.ID != u.Message.ReplyMsg.From.ID
	case WhenType_BotCommand:
		return slices.IndexFunc(u.Message.Entities, func(m MessageEntity) bool {
			return m.Type == "bot_command"
		}) >= 0
	case WhenType_SoloMessage:
		if len(u.Message.Entities) > 0 {
			return false
		}
		return u.Message.ReplyMsg.From.ID == 0
	case WhenType_Reply:
		return u.Message.ReplyMsg.From.ID != 0
	}
	return true
}

func process_top_message(u Update) {
	var msg string
	var users []Top
	for _, user := range users_data.Users {
		users = append(users, Top{user.Name, user.Gratz})
	}

	sort.Slice(users, func(i, j int) bool {
		return users[i].Amount > users[j].Amount
	})

	for i, user := range users {
		msg += strconv.Itoa(i+1) + ". " + user.UserName + ": " + strconv.Itoa(user.Amount) + "\n"
	}
	make_request_send_message_to_chat(u.Message.Chat.ID, msg)
}

func perform_action(action Action, u Update) {
	switch action.Type {
	case ActionType_SendReaction:
		switch action.SendTo {
		case ActionUserType_SendUser:
			err := make_reaction_request(u.Message.MessageID, u.Message.Chat.ID, string_to_reaction_type(action.Value))
			if err != nil {
				fmt.Println("[perform_reaction][ActionType_SendReaction][SendUser]:", err)
				return
			}
		case ActionUserType_ReplyUser:
			err := make_reaction_request(u.Message.ReplyMsg.MessageID, u.Message.Chat.ID, string_to_reaction_type(action.Value))
			if err != nil {
				fmt.Println("[perform_reaction][ActionType_SendReaction][ReplyUser]:", err)
				return
			}
		}
	case ActionType_AppendGratz:
		switch action.SendTo {
		case ActionUserType_SendUser:
			send_user := u.Message.From
			append_gratz_to_user(send_user)
		case ActionUserType_ReplyUser:
			reply_user := u.Message.ReplyMsg.From
			append_gratz_to_user(reply_user)
		}
	case ActionType_Top:
		process_top_message(u)
	case ActionType_SendMessage:
		make_request_send_message_to_chat(u.Message.Chat.ID, action.Value)
	}
}
