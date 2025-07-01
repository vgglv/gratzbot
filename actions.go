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

func loadActionsFromFile() error {
	commands_file, err := os.ReadFile("assets/commands.json")
	if err != nil {
		return err
	}
	if err = json.Unmarshal(commands_file, &commandsDB); err != nil {
		return err
	}
	if config.IsDebug {
		fmt.Printf("%+v\n", commandsDB)
	}
	return nil
}

func processCommandOnUpdate(u Update) {
	for _, command := range commandsDB {
		if !containsExactWord(u.Message.Text, command.TextContains) {
			continue
		}
		var conditionFulfilled bool = true
		for _, w := range command.Conditions {
			if !checkIfConditionFulfilled(w, u) {
				conditionFulfilled = false
				break
			}
		}
		if !conditionFulfilled {
			continue
		}
		for _, action := range command.Actions {
			performActionOnUpdate(action, u)
		}
	}
}

func checkIfConditionFulfilled(cond Condition, u Update) bool {
	switch cond {
	case Condition_Himself:
		return u.Message.From.Id == u.Message.ReplyMsg.From.Id
	case Condition_NotHimself:
		return u.Message.From.Id != u.Message.ReplyMsg.From.Id
	case Condition_BotCommand:
		return slices.IndexFunc(u.Message.Entities, func(m MessageEntity) bool {
			return m.Type == "bot_command"
		}) >= 0
	case Condition_SoloMessage:
		if len(u.Message.Entities) > 0 {
			return false
		}
		return u.Message.ReplyMsg.From.Id == 0
	case Condition_Reply:
		return u.Message.ReplyMsg.From.Id != 0
	}
	return true
}

func processTopUpdate(u Update) {
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
	sendMessageRequest(u.Message.Chat.Id, msg, Message_Nullopt)
}

func performActionOnUpdate(action Action, u Update) {
	switch action.Type {
	case ActionType_SendReaction:
		switch action.SendTo {
		case ActionUserType_SendUser:
			err := sendMessageReactionRequest(u.Message.MessageId, u.Message.Chat.Id, stringToReactionTypeSlice(action.Value))
			if err != nil {
				fmt.Println("[perform_reaction][ActionType_SendReaction][SendUser]:", err)
				return
			}
		case ActionUserType_ReplyUser:
			err := sendMessageReactionRequest(u.Message.ReplyMsg.MessageId, u.Message.Chat.Id, stringToReactionTypeSlice(action.Value))
			if err != nil {
				fmt.Println("[perform_reaction][ActionType_SendReaction][ReplyUser]:", err)
				return
			}
		}
	case ActionType_AppendGratz:
		switch action.SendTo {
		case ActionUserType_SendUser:
			send_user := u.Message.From
			appendGratzToUser(send_user)
		case ActionUserType_ReplyUser:
			reply_user := u.Message.ReplyMsg.From
			appendGratzToUser(reply_user)
		}
	case ActionType_Top:
		processTopUpdate(u)
	case ActionType_SendMessage:
		switch action.SendTo {
		case ActionUserType_SendUser:
			sendMessageRequest(u.Message.Chat.Id, action.Value, u.Message.MessageId)
		case ActionUserType_ReplyUser:
			//not implemented
		case ActionUserType_Chat:
			sendMessageRequest(u.Message.Chat.Id, action.Value, Message_Nullopt)
		}
	}
}
