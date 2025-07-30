#pragma once
#include "nlohmann/json.hpp"
#include <string>
#include <optional>
#include <vector>
#include <map>

using nlohmann::json;

struct Config {
    int request_timeout;
    int sleep_time;
    std::string url_route;
};

enum class UserType {
    SEND_USER,
    REPLY_USER,
};

enum class ConditionType {
    REPLY,
    NOT_HIMSELF,
    HIMSELF,
    BOT_COMMAND,
    SOLO_MESSAGE,
};

struct Action {
    std::string type;
    std::optional<std::string> value;
    std::optional<UserType> send_to;
};


struct Command {
    std::string text_contains;
    std::vector<ConditionType> conditions;
    std::vector<Action> actions;
};

struct LocalUser {
    int gratz;
    std::string name;
};

struct UsersDB {
    unsigned long int last_update;
    std::map<std::string, LocalUser> Users;
};

struct Chat {
    int id;
};

struct ReactionType {
    std::string type;
    std::string emoji;
};

struct User {
    int id;
    bool is_bot;
    std::string first_name;
};

struct MessageReaction {
    Chat chat;
    int message_id;
    std::optional<User> user;
    std::vector<ReactionType> old_reaction;
    std::vector<ReactionType> new_reaction;
};

struct MessageEntity {
    std::string type;
    int offset;
    int length;
};

struct ReplyMessage {
    int message_id;
    std::optional<User> from;
};

struct Message {
    int message_id;
    std::optional<User> from;
    std::vector<MessageEntity> entities;
    std::string text;
    Chat chat;
    std::optional<ReplyMessage> reply_to_message;
};

struct Update {
    int update_id;
    std::optional<MessageReaction> message_reaction;
    std::optional<Message> message;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Config, request_timeout, sleep_time, url_route);
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(LocalUser, gratz, name);
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(UsersDB, last_update, Users);
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Chat, id);
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(ReactionType, type, emoji);
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(User, id, is_bot, first_name);
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(MessageEntity, type, offset, length);

NLOHMANN_JSON_SERIALIZE_ENUM( UserType, {
    {UserType::SEND_USER, "send_user"},
    {UserType::REPLY_USER, "reply_user"},
});

NLOHMANN_JSON_SERIALIZE_ENUM( ConditionType, {
    {ConditionType::REPLY, "reply"},
    {ConditionType::NOT_HIMSELF, "not_himself"},
    {ConditionType::HIMSELF, "himself"},
    {ConditionType::BOT_COMMAND, "bot_command"},
    {ConditionType::SOLO_MESSAGE, "solo_command"},
});

inline void to_json(json& j, const Action& p) {
    j = json{
        {"type", p.type}
    };
    if (p.send_to) {
        j["send_to"] = p.send_to.value();
    }
    if (p.value) {
        j["value"] = p.value.value();
    }
}
inline void from_json(const json& j, Action& p) {
    p.type = j["type"].get<std::string>();
    if (j.contains("send_to")) {
        p.send_to = j["send_to"].get<UserType>();
    }
    if (j.contains("value")) {
        p.value = j["value"].get<std::string>();
    }
}

inline void to_json(json& j, const Command& p) {
    j = json{
        {"text_contains", p.text_contains}
    };
    for (const auto& a : p.actions) {
        j["actions"].emplace_back(a);
    }
    for (const auto& c : p.conditions) {
        j["when"].emplace_back(c);
    }
}
inline void from_json(const json& j, Command& p) {
    p.text_contains = j["text_contains"].get<std::string>();
    for (const auto& a : j["actions"]) {
        p.actions.emplace_back(a.get<Action>());
    }
    for (const auto& a : j["when"]) {
        p.conditions.emplace_back(a.get<ConditionType>());
    }
}

inline void to_json(json& j, const MessageReaction& p) {
    j = json{
        {"chat", p.chat},
        {"message_id", p.message_id}
    };
    if (p.user) {
        j["user"] = p.user.value();
    }
    for (const auto& reaction : p.old_reaction) {
        j["old_reaction"].emplace_back(reaction);
    }
    for (const auto& reaction : p.new_reaction) {
        j["new_reaction"].emplace_back(reaction);
    }
}
inline void from_json(const json& j, MessageReaction& p) {
    p.chat = j["chat"].get<Chat>();
    p.message_id = j["message_id"].get<int>();
    if (j.contains("user")) {
        p.user = j["user"].get<User>();
    }
    if (j.contains("old_reaction")) {
        for (const auto& reaction_json : j["old_reaction"]) {
            p.old_reaction.emplace_back(reaction_json.get<ReactionType>());
        }
    }
    if (j.contains("new_reaction")) {
        for (const auto& reaction_json : j["new_reaction"]) {
            p.new_reaction.emplace_back(reaction_json.get<ReactionType>());
        }
    }
}

inline void to_json(json& j, const ReplyMessage& p) {
    j = json{
        {"message_id", p.message_id}
    };
    if (p.from) {
        j["from"] = p.from.value();
    }
}
inline void from_json(const json& j, ReplyMessage& p) {
    p.message_id = j["message_id"].get<int>();
    if (j.contains("from")) {
        p.from = j["from"].get<User>();
    }
}

inline void to_json(json& j, const Message& p) {
    j = json{
        {"message_id", p.message_id},
        {"text", p.text},
        {"chat", p.chat},
        {"entities", p.entities}
    };
    if (p.from) {
        j["from"] = p.from.value();
    }
    if (p.reply_to_message) {
        j["reply_to_message"] = p.reply_to_message.value();
    }
//    for (const auto& entity : p.entities) {
//        j["entities"].emplace_back(entity);
//    }
}
inline void from_json(const json& j, Message& p) {
    p.message_id = j["message_id"].get<int>();
    p.text = j["text"].get<std::string>();
    p.chat = j["chat"].get<Chat>();
    if (j.contains("entities")) {
        p.entities = j["entities"].get<std::vector<MessageEntity>>();
    }
    if (j.contains("from")) {
        p.from = j["from"].get<User>();
    }
    if (j.contains("reply_to_message")) {
        p.reply_to_message = j["reply_to_message"].get<ReplyMessage>();
    }
}

inline void to_json(json& j, const Update& p) {
    j = json{
        {"update_id", p.update_id},
    };
    if (p.message_reaction) {
        j["message_reaction"] = p.message_reaction.value();
    }
    if (p.message) {
        j["message"] = p.message.value();
    }
}
inline void from_json(const json& j, Update& p) {
    p.update_id = j["update_id"].get<int>();
    if (j.contains("message_reaction")) {
        p.message_reaction = j["message_reaction"].get<MessageReaction>();
    }
    if (j.contains("message")) {
        p.message = j["message"].get<Message>();
    }
}
