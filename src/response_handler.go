package main

import (
	"fmt"
	"slices"
	"strings"
)

func ResponseHandler_processUpdates(updates []Update, offset int) {
	for _, update := range updates {
//		if update.Message.Chat.ID != channel_id {
//			continue
//		}
		if update.ID <= offset {
			continue
		}
		fmt.Println(update)
		lowercaseText := strings.ToLower(update.Message.Text)
		if lowercaseText == "грац" {
			//ResponseHandler_processGratzMsg(update)
			continue
		}
		var is_not_bot_command bool = slices.IndexFunc(update.Message.Entities, func(m MessageEntity) bool {
			return m.Type == "bot_command"
		}) < 0
		mention_array_id := slices.IndexFunc(update.Message.Entities, func(m MessageEntity) bool {
			return m.Type == "mention"
		})
		if mention_array_id >= 0 {
			//ResponseHandler_processMention(update, mention_array_id)
			continue
		}
		if is_not_bot_command {
			//ResponseHandler_processNonCommandUpdate(update.Message)
			continue
		}
		if strings.Contains(update.Message.Text, "gratz") {
			//ResponseHandler_processGratzMsg(update)
			continue
		}
		if strings.Contains(update.Message.Text, "top") {
			//ResponseHandler_processTopMsg(update)
		}
	}
}
