package main

import (
	"fmt"
	"slices"
	"sort"
	"strconv"
	"strings"
)

const reaction_ok string = "👌"
const reaction_clown string = "🤡"
const reaction_fire string = "🔥"

func process_telegram_updates(updates []Update, offset int) {
	for _, update := range updates {
		if !is_debug {
			if update.Message.Chat.ID != channel_id {
				continue
			}
		}
		if update.ID <= offset {
			continue
		}
		if is_debug {
			fmt.Println(update)
		}
		lowercaseText := strings.ToLower(update.Message.Text)
		if lowercaseText == "грац" {
			process_gratz_message(update)
			continue
		}
		if lowercaseText == "ахуй" {
			err := make_reaction_request(update.Message.MessageID, update.Message.Chat.ID, string_to_reaction_type(reaction_fire))
			if err != nil {
				fmt.Println("Error sending reaction", err)
			}
		}
		var is_not_bot_command bool = slices.IndexFunc(update.Message.Entities, func(m MessageEntity) bool {
			return m.Type == "bot_command"
		}) < 0
		//mention_array_id := slices.IndexFunc(update.Message.Entities, func(m MessageEntity) bool {
		//	return m.Type == "mention"
		//})
		//if mention_array_id >= 0 {
		//	//ResponseHandler_processMention(update, mention_array_id)
		//	continue
		//}
		if is_not_bot_command {
			//ResponseHandler_processNonCommandUpdate(update.Message)
			continue
		}
		if strings.Contains(update.Message.Text, "gratz") {
			process_gratz_message(update)
			continue
		}
		if strings.Contains(update.Message.Text, "top") {
			process_top_message(update)
		}
	}
}

func process_gratz_message(u Update) {
	user := u.Message.ReplyMsg.From
	if user.ID == 0 {
		if is_debug {
			fmt.Println("User id is 0, data:", user)
		}
		return
	}
	send_user := u.Message.From
	if user.ID == send_user.ID && !is_debug {
		err := make_reaction_request(u.Message.MessageID, u.Message.Chat.ID, string_to_reaction_type(reaction_clown))
		if err != nil {
			fmt.Println("Error sending reaction", err)
		}
		return
	}
	append_gratz_to_user(user)
	err := make_reaction_request(u.Message.MessageID, u.Message.Chat.ID, string_to_reaction_type(reaction_ok))
	if err != nil {
		fmt.Println("Error sending reaction", err)
	}
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
