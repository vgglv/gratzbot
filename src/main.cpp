#include <fstream>
#include <iostream>
#include "types.hpp"

using namespace nlohmann;

int main() {
    std::ifstream config_file("assets/config.json");
    json config_json = json::parse(config_file);
    Config config = config_json.get<Config>();

    std::ifstream commands_file("assets/commands.json");
    json commands_json = json::parse(commands_file);
    std::vector<Command> commands = commands_json.get<std::vector<Command>>();

    auto printAction = [](Action act) {
        std::cout << "\tAction: " << act.type << "\n";
        if (act.send_to) {
            std::cout << "\tSend to: " << static_cast<int>(act.send_to.value()) << "\n";
        }
        if (act.value) {
            std::cout << "\tValue: " << act.value.value() << "\n";
        }
    };

    auto printCommand = [printAction](Command cmd) {
        std::cout << "Text contains: " << cmd.text_contains << "\n";
        for (const auto& when : cmd.conditions) {
            std::cout << "When: " << static_cast<int>(when) << "\n";
        }
        for (const auto& a : cmd.actions) {
            printAction(a);
        }
    };

    for (const auto& cmd : commands) {
        printCommand(cmd);
    }
}