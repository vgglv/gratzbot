#pragma once
#include <string>
#include <optional>
#include "nlohmann/detail/macro_scope.hpp"
#include "nlohmann/json.hpp"

using namespace nlohmann;

struct Config {
    int request_timeout;
    int sleep_time;
    std::string url_route;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Config, request_timeout, sleep_time, url_route);

enum class UserType {
    SEND_USER,
    REPLY_USER,
};

NLOHMANN_JSON_SERIALIZE_ENUM( UserType, {
    {UserType::SEND_USER, "send_user"},
    {UserType::REPLY_USER, "reply_user"},
});


struct Action {
    std::string type;
    std::optional<std::string> value;
    std::optional<UserType> send_to;
};

enum class ConditionType {
    REPLY,
    NOT_HIMSELF,
    HIMSELF,
    BOT_COMMAND,
    SOLO_MESSAGE,
};

NLOHMANN_JSON_SERIALIZE_ENUM( ConditionType, {
    {ConditionType::REPLY, "reply"},
    {ConditionType::NOT_HIMSELF, "not_himself"},
    {ConditionType::HIMSELF, "himself"},
    {ConditionType::BOT_COMMAND, "bot_command"},
    {ConditionType::SOLO_MESSAGE, "solo_command"},
});

struct Command {
    std::string text_contains;
    std::vector<ConditionType> conditions;
    std::vector<Action> actions;
};

void to_json(json& j, const Action& p) {
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

void from_json(const json& j, Action& p) {
    p.type = j["type"].get<std::string>();
    if (j.contains("send_to")) {
        p.send_to = j["send_to"].get<UserType>();
    }
    if (j.contains("value")) {
        p.value = j["value"].get<std::string>();
    }
}

void to_json(json& j, const Command& p) {
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

void from_json(const json& j, Command& p) {
    p.text_contains = j["text_contains"].get<std::string>();
    for (const auto& a : j["actions"]) {
        p.actions.emplace_back(a.get<Action>());
    }
    for (const auto& a : j["when"]) {
        p.conditions.emplace_back(a.get<ConditionType>());
    }
}

struct User {
    int gratz;
    std::string name;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(User, gratz, name);

struct UsersDB {
    unsigned long int last_update;
    std::map<std::string, User> users;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(UsersDB, last_update, users);