package main

type ActionType string
type ActionUserType string
type Condition string

const (
	ActionType_SendReaction ActionType = "send_reaction"
	ActionType_AppendGratz  ActionType = "append_gratz"
	ActionType_Top          ActionType = "send_gratz_top"
	ActionType_SendMessage  ActionType = "send_message"

	ActionUserType_SendUser  ActionUserType = "send_user"
	ActionUserType_ReplyUser ActionUserType = "reply_user"
	ActionUserType_Chat      ActionUserType = "chat"

	Condition_Reply       Condition = "reply"
	Condition_BotCommand  Condition = "bot_command"
	Condition_SoloMessage Condition = "solo_message"
	Condition_NotHimself  Condition = "not_himself"
	Condition_Himself     Condition = "himself"

	Message_Nullopt = -1
)

type Config struct {
	BotToken       string
	ChannelId      int
	IsDebug        bool
	SleepTime      int    `json:"sleep_time"`
	RequestTimeout int    `json:"request_timeout"`
	UrlRoute       string `json:"url_route"`
}

type Action struct {
	Type   ActionType     `json:"type"`
	Value  string         `json:"value"`
	SendTo ActionUserType `json:"send_to"`
}

type Command struct {
	TextContains string      `json:"text_contains"`
	Conditions   []Condition `json:"conditions,omitempty"`
	Actions      []Action    `json:"actions"`
	Probability  int         `json:"probability,omitempty"`
}

// ##### TELEGRAM ######

type SendMessagePayload struct {
	ChatId      string          `json:"chat_id"`
	Text        string          `json:"text"`
	ReplyParams ReplyParameters `json:"reply_parameters,omitempty"`
}

type ReplyParameters struct {
	MessageId int `json:"message_id"`
	ChatId    int `json:"chat_id,omitempty"`
}

type Chat struct {
	Id int `json:"id"`
}

type MessageEntity struct {
	Type   string `json:"type"`
	Offset int    `json:"offset"`
	Length int    `json:"length"`
}

type ReplyMessage struct {
	MessageId int  `json:"message_id"`
	From      User `json:"from,omitempty"`
}

type Message struct {
	MessageId int             `json:"message_id"`
	From      User            `json:"from,omitempty"`
	Entities  []MessageEntity `json:"entities,omitempty"`
	Text      string          `json:"text,omitempty"`
	Chat      Chat            `json:"chat"`
	ReplyMsg  ReplyMessage    `json:"reply_to_message,omitempty"`
}

type User struct {
	Id        int    `json:"id"`
	IsBot     bool   `json:"is_bot"`
	FirstName string `json:"first_name"`
}

type ReactionType struct {
	Type  string `json:"type"`
	Emoji string `json:"emoji"`
}

type MessageReactionUpdated struct {
	Chat        Chat           `json:"chat"`
	MessageId   int            `json:"message_id"`
	User        User           `json:"user,omitempty"`
	OldReaction []ReactionType `json:"old_reaction"`
	NewReaction []ReactionType `json:"new_reaction"`
}

type Update struct {
	UpdateId        int                    `json:"update_id"`
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

type Top struct {
	UserName string
	Amount   int
}
