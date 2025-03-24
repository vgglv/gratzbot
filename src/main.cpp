#include <cstdlib>
#include <fstream>
#include <iostream>
#include <thread>
#include "cpr/cpr.h"
#include "types.hpp"

using namespace nlohmann;

int main() {
    auto bot_api_key = getenv("gratz_bot_api_key");
    if (!bot_api_key) {
        std::cerr << "Error: could not find bot api key\n";
        return 1;
    }
    std::ifstream config_file("assets/config.json");
    json config_json = json::parse(config_file);
    Config config = config_json.get<Config>();
    config.url_route += bot_api_key;

    std::ifstream commands_file("assets/commands.json");
    json commands_json = json::parse(commands_file);
    std::vector<Command> commands = commands_json.get<std::vector<Command>>();

//    auto printAction = [](Action act) {
//        std::cout << "\tAction: " << act.type << "\n";
//        if (act.send_to) {
//            std::cout << "\tSend to: " << static_cast<int>(act.send_to.value()) << "\n";
//        }
//        if (act.value) {
//            std::cout << "\tValue: " << act.value.value() << "\n";
//        }
//    };
//
//    auto printCommand = [printAction](Command cmd) {
//        std::cout << "Text contains: " << cmd.text_contains << "\n";
//        for (const auto& when : cmd.conditions) {
//            std::cout << "When: " << static_cast<int>(when) << "\n";
//        }
//        for (const auto& a : cmd.actions) {
//            printAction(a);
//        }
//    };
//
//    for (const auto& cmd : commands) {
//        printCommand(cmd);
//    }

    std::ifstream users_file("users.json");
    json users_json = json::parse(users_file);
    UsersDB users_db = users_json.get<UsersDB>();

    json request_update_payload;
    request_update_payload["offset"] = 1;
    request_update_payload["timeout"] = 10;
    request_update_payload["allowed_updates"].emplace_back("message");

//    cpr::Response r = cpr::Get(cpr::Url{"https://api.github.com/repos/whoshuu/cpr/contributors"},
//                               cpr::Authentication{"user", "pass", cpr::AuthMode::BASIC},
//                               cpr::Parameters{{"anon", "true"}, {"key", "value"}});
//    std::cout << "Status code: " << r.status_code << '\n';
//    std::cout << "Header:\n";
//    for (const std::pair<const std::basic_string<char>, std::basic_string<char>>& kv : r.header) {
//        std::cout << '\t' << kv.first << ':' << kv.second << '\n';
//    }
//    std::cout << "Text: " << r.text << '\n';

    cpr::Response r = cpr::Post(cpr::Url{config.url_route + "/getUpdates"}, cpr::Body{request_update_payload.dump()},
        cpr::Parameters{{"Content-Type", "application/json"}});
    std::cout << r.status_code << "\n";
    std::cout << r.text << "\n";


//    using namespace std::chrono_literals;

//    while(true) {
//        std::this_thread::sleep_for(5s);
//    }

//    for (const auto& [id, data] : users_db.users) {
//        std::cout << "ID: " << id << " gratz: " << data.gratz << " name " << data.name << "\n";
//    }
    return 0;
}
