package main

type Stock struct {
	Name             string `json:"name"`
	Stocks_available int    `json:"stocks_available"`
}

// ##### TELEGRAM ######

type SendMessagePayload struct {
	ChatId string `json:"chat_id"`
	Text   string `json:"text"`
}

type Chat struct {
	ID int `json:"id"`
}

type MessageEntity struct {
	Type   string `json:"type"`
	Offset int    `json:"offset"`
	Length int    `json:"length"`
}

type ReplyMessage struct {
	MessageID int  `json:"message_id"`
	From      User `json:"from,omitempty"`
}

type Message struct {
	MessageID int             `json:"message_id"`
	From      User            `json:"from,omitempty"`
	Entities  []MessageEntity `json:"entities,omitempty"`
	Text      string          `json:"text,omitempty"`
	Chat      Chat            `json:"chat"`
	ReplyMsg  ReplyMessage    `json:"reply_to_message,omitempty"`
}

type User struct {
	ID        int    `json:"id"`
	IsBot     bool   `json:"is_bot"`
	FirstName string `json:"first_name"`
}

type ReactionType struct {
	Type  string `json:"type"`
	Emoji string `json:"emoji"`
}

type MessageReactionUpdated struct {
	Chat        Chat           `json:"chat"`
	Message_id  int            `json:"message_id"`
	User        User           `json:"user,omitempty"`
	OldReaction []ReactionType `json:"old_reaction"`
	NewReaction []ReactionType `json:"new_reaction"`
}

type Update struct {
	ID              int                    `json:"update_id"`
	MessageReaction MessageReactionUpdated `json:"message_reaction,omitempty"`
	Message         Message                `json:"message,omitempty"`
}

// ##### local save structs #####

type UsersData struct {
	LastUpdate int              `json:"last_update"`
	Users      map[int]UserInfo `json:"Users"`
}

type UserInfo struct {
	Gratz int    `json:"gratz"`
	Name  string `json:"name"`
}

type UpdateResponsePayload struct {
	Result []Update
}

type SendMessageResponsePayload struct {
	Result Message `json:"result"`
}

type RequestUpdatePayload struct {
	Offset         string   `json:"offset"`
	Timeout        string   `json:"timeout"`
	AllowedUpdates []string `json:"allowed_updates"`
}

type CustomError struct {
	message string
}

func (e *CustomError) Error() string {
	return e.message
}

type Top struct {
	UserName string
	Amount   int
}
