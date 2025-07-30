#include "App.hpp"
#include <fstream>
#include "cpr/cpr.h"
#include "types.hpp"
#include "nlohmann/json.hpp"
#include "env.hpp"

namespace app {
    int App::run() {
        gratzbot::EnvContainer env;
        env.parseDotEnv();
        auto bot_api_key = env.getEnv("gratzbot_api_key");
        if (!bot_api_key.has_value()) {
            std::println("Bot api key empty");
            return -1;
        }

        std::ifstream config_file("assets/config.json");
        json config_json = json::parse(config_file);
        Config config = config_json.get<Config>();
        config.url_route += bot_api_key.value();

        std::ifstream users_file("users.json");
        json users_json = json::parse(users_file);
        UsersDB users_db = users_json.get<UsersDB>();

        std::println("Users db: {}", nlohmann::json{users_db}.dump());

        std::chrono::seconds sleep_time_in_seconds(config.sleep_time);
        while(true) {
            std::this_thread::sleep_for(sleep_time_in_seconds);

            json request_update_payload;
            request_update_payload["offset"] = users_db.last_update + 1;
            request_update_payload["timeout"] = config.sleep_time;
            request_update_payload["allowed_updates"].emplace_back("message");

            cpr::Response r = cpr::Post(
                cpr::Url{config.url_route + "/getUpdates"},
                cpr::Body{request_update_payload.dump()},
                cpr::Parameters{{"Content-Type", "application/json"}}
            );
            json answer = json::parse(r.text);
            std::vector<Update> updates = answer["result"].get<std::vector<Update>>();
            for (const auto& update : updates) {
                std::println("Update id: {}", update.update_id);
                users_db.last_update = update.update_id;
            }
        }
    }
}