#include "CommandExecutor.hpp"
#include <fstream>

namespace gratzbot {
    CommandExecutor::CommandExecutor() {
        std::ifstream commands_file("assets/commands.json");
        json commands_json = json::parse(commands_file);
        commands.clear();
        commands = commands_json.get<std::vector<Command>>();
    }

    CommandExecutor::~CommandExecutor() {

    }

    void CommandExecutor::processUpdate(const Update& u) {

    }
}